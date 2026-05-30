"""FastAPI application entry point for Box Smart Inbox."""

import asyncio
import io
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.shared.config import Config
from backend.shared.logging import setup_logging
from backend.shared.types import IngestedDocument, ProcessingResult
from backend.shared.database import db
from backend.domain_1_email import routes as domain1_routes
from backend.domain_2_classifier import routes as domain2_routes
from backend.domain_3_box_integration import routes as domain3_routes
from backend.orchestration import routes as orchestration_routes

# Setup logging
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Box Smart Inbox",
    description="AI-powered document orchestration with signature tracking",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INBOX_POLL_INTERVAL = 60  # seconds between inbox checks


async def _process_inbox_once():
    """Sort all PDFs currently in the Box Inbox folder."""
    from backend.domain_3_box_integration.box_client import BoxClient
    from backend.domain_2_classifier.service import ClassificationService
    from backend.domain_3_box_integration.metadata import MetadataManager
    from backend.domain_3_box_integration.tasks import TaskManager, REVIEWER_EMAIL_MAPPING
    from backend.domain_3_box_integration.notifications import NotificationManager
    from backend.shared.config import FOLDER_MAPPING, REVIEWER_MAPPING
    from backend.domain_1_email.textract_parser import get_textract_parser
    from datetime import datetime, timezone

    inbox_folder_id = Config.BOX_INBOX_FOLDER_ID
    if not inbox_folder_id:
        return

    box_client = BoxClient()

    try:
        files = await box_client.list_files(inbox_folder_id)
    except Exception as e:
        logger.warning(f"Inbox poll: could not list files: {e}")
        return

    pdfs = [f for f in files if f["name"].lower().endswith(".pdf")]
    if not pdfs:
        return

    logger.info(f"Inbox poll: found {len(pdfs)} PDF(s) to sort")

    for file_info in pdfs:
        file_id   = file_info["id"]
        file_name = file_info["name"]
        try:
            # Download
            file_bytes = await box_client.download_file(file_id)

            # Extract text
            extracted_text = await get_textract_parser().extract_pdf_text(file_bytes, file_name)
            if not extracted_text:
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                        extracted_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
                except Exception:
                    extracted_text = f"[Could not extract text from {file_name}]"

            # Classify
            document = IngestedDocument(
                filename=file_name,
                content=extracted_text,
                content_type="application/pdf",
                source="box_file_request",
                raw_file_bytes=file_bytes,
            )
            classifier = ClassificationService()
            classification = await classifier.classify(document)

            # Destination folder
            base_path = FOLDER_MAPPING.get(classification.doc_type, "/Other Documents")
            now = datetime.now(timezone.utc)
            if classification.doc_type in ("invoice", "contract", "receipt", "purchase_order"):
                destination = f"{base_path}/{now.year}/{now.strftime('%B')}"
            else:
                destination = base_path

            # Move file
            dest_folder_id = await box_client.get_or_create_folder(destination)
            await box_client.move_file(file_id, dest_folder_id)

            logger.info(
                f"Inbox poll: sorted '{file_name}' → {destination} "
                f"({classification.doc_type} {classification.confidence:.0%})"
            )

            # Metadata (non-fatal)
            try:
                metadata = MetadataManager().build_metadata_dict(classification)
                await box_client.apply_metadata(file_id, metadata)
            except Exception:
                pass

            # Task + Slack (non-fatal)
            try:
                reviewer_role  = REVIEWER_MAPPING.get(classification.doc_type)
                reviewer_email = REVIEWER_EMAIL_MAPPING.get(reviewer_role) if reviewer_role else None
                task_id = await TaskManager(box_client).create_review_task(
                    file_id=file_id,
                    doc_type=classification.doc_type,
                    assigned_to_email=reviewer_email,
                )
                await NotificationManager().send_notifications(
                    document_id=document.id,
                    doc_type=classification.doc_type,
                    assigned_to_email=reviewer_email or "",
                    channels=["slack"],
                    metadata={
                        "box_file_id": file_id,
                        "confidence": classification.confidence,
                        "vendor": classification.extracted_fields.get("vendor", ""),
                        "amount": classification.extracted_fields.get("amount"),
                    },
                )
            except Exception as e:
                logger.warning(f"Inbox poll: task/notification failed (non-fatal): {e}")

        except Exception as e:
            logger.error(f"Inbox poll: failed to process '{file_name}': {e}")


async def _inbox_poller():
    """Background loop: check inbox every INBOX_POLL_INTERVAL seconds."""
    await asyncio.sleep(10)  # short delay so app finishes starting up
    while True:
        try:
            await _process_inbox_once()
        except Exception as e:
            logger.error(f"Inbox poller error: {e}")
        await asyncio.sleep(INBOX_POLL_INTERVAL)


# Database startup and shutdown
@app.on_event("startup")
async def startup():
    """Initialize database connection and start background inbox poller."""
    logger.info("Starting Box Smart Inbox application")
    if Config.DEMO_MODE:
        logger.info("DEMO_MODE enabled - skipping database connection")
    else:
        try:
            await db.connect()
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    # Start background inbox poller
    if Config.BOX_INBOX_FOLDER_ID:
        asyncio.create_task(_inbox_poller())
        logger.info(
            f"Inbox poller started — checking every {INBOX_POLL_INTERVAL}s "
            f"(folder {Config.BOX_INBOX_FOLDER_ID})"
        )
    else:
        logger.warning("BOX_INBOX_FOLDER_ID not set — inbox poller disabled")


@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown."""
    logger.info("Shutting down Box Smart Inbox application")
    if not Config.DEMO_MODE:
        await db.disconnect()
        logger.info("Database disconnected")


# Include domain routers
app.include_router(domain1_routes.router, tags=["domain-1"])
app.include_router(domain2_routes.router, tags=["domain-2"])
app.include_router(domain3_routes.router, tags=["domain-3"])
app.include_router(orchestration_routes.router, tags=["orchestration"])


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "box-smart-inbox",
        "environment": Config.ENVIRONMENT,
    }


@app.get("/status")
async def get_status() -> dict:
    """
    Get system status and database statistics.

    Returns:
        dict: Status including documents in pipeline, success rate, etc.
    """
    try:
        total_docs = await db.fetch_val("SELECT COUNT(*) FROM documents")
        completed_docs = await db.fetch_val(
            "SELECT COUNT(*) FROM documents WHERE status = 'complete'"
        )
        success_rate = (completed_docs / total_docs * 100) if total_docs > 0 else 0

        return {
            "status": "operational",
            "documents_total": total_docs,
            "documents_completed": completed_docs,
            "success_rate": f"{success_rate:.1f}%",
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            "status": "operational",
            "documents_total": 0,
            "documents_completed": 0,
            "success_rate": "0.0%",
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        log_level=Config.LOG_LEVEL.lower(),
    )
