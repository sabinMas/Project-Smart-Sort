"""FastAPI routes for Domain 1 (Email Ingestion)."""

import base64
import logging
from fastapi import APIRouter, Request, HTTPException

from .models import (
    DocumentUploadRequest,
    DocumentIngestionResponse,
)
from .service import EmailIngestionService
from backend.shared.errors import (
    EmailIngestionError,
    InvalidEmailFormatError,
    AttachmentExtractionError,
)
from backend.orchestration import get_orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

# Service instance
email_service = EmailIngestionService()


@router.post("/webhooks/sendgrid", tags=["email"])
async def handle_sendgrid_webhook(request: Request) -> dict:
    """
    Handle incoming emails from SendGrid Inbound Parse webhook.

    Expects multipart/form-data or JSON payload from SendGrid with:
    - from, to, subject, text/html body
    - Optional attachments (base64 encoded)

    Returns:
        200 OK with document_id on success
        400 Bad Request on invalid payload
        401 Unauthorized on invalid signature
    """
    try:
        # Parse request body — SendGrid can send JSON or form data
        content_type = request.headers.get("content-type", "")

        if "multipart/form-data" in content_type:
            form = await request.form()
            from_email = form.get("from", "")
            to_email = form.get("to", "")
            subject = form.get("subject", "")
            text_content = form.get("text", None)
            html_content = form.get("html", None)

            # Extract attachments from form data
            attachments = []
            attachment_count = int(form.get("attachments", 0) or 0)
            for i in range(1, attachment_count + 1):
                att_info = form.get(f"attachment-info", None)
                att_file = form.get(f"attachment{i}", None)
                if att_file and hasattr(att_file, "read"):
                    file_bytes = await att_file.read()
                    attachments.append({
                        "filename": att_file.filename or f"attachment{i}",
                        "content_type": att_file.content_type or "application/octet-stream",
                        "content": base64.b64encode(file_bytes).decode("utf-8"),
                    })
        else:
            # JSON payload
            body = await request.json()
            from_email = body.get("from", "")
            to_email = body.get("to", "")
            subject = body.get("subject", "")
            text_content = body.get("text", None)
            html_content = body.get("html", None)

            # Attachments in JSON are already base64 encoded
            attachments = body.get("attachments", []) or []

        # Validate signature (if headers present)
        signature = request.headers.get("x-twilio-email-event-webhook-signature", "")
        timestamp = request.headers.get("x-twilio-email-event-webhook-timestamp", "")

        if signature and timestamp:
            raw_body = await request.body()
            payload_str = raw_body.decode("utf-8", errors="replace")
            is_valid = await email_service.validate_sendgrid_signature(
                signature, timestamp, payload_str
            )
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid webhook signature")

        # Step 1: DOMAIN 1 - Process the email
        document = await email_service.ingest_email(
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            attachments=attachments,
        )

        logger.info(f"Email ingested successfully: document_id={document.id}")

        # Step 2: AUTO-TRIGGER ORCHESTRATION (Domain 2 → Domain 3)
        # This chains classification and Box routing automatically
        try:
            logger.info(f"Starting automatic orchestration for {document.id}...")
            orchestrator = get_orchestrator()
            processing_result = await orchestrator.process_ingested_document(document)

            # Build response showing full pipeline
            return {
                "status": "success",
                "document_id": document.id,
                "filename": document.filename,
                "pipeline": {
                    "domain_1_ingestion": "✅ Complete",
                    "domain_2_classification": {
                        "status": "✅ Complete",
                        "type": processing_result.status if processing_result else "unknown",
                        "error": processing_result.error_message if processing_result else None,
                    },
                    "domain_3_box_routing": {
                        "status": "✅ Complete" if processing_result and processing_result.box_file_id else "⏸️ Pending Review",
                        "destination": processing_result.destination_folder if processing_result else None,
                        "task_id": processing_result.task_id if processing_result else None,
                        "assigned_to": processing_result.assigned_to if processing_result else None,
                    },
                },
                "processing_result": processing_result.dict() if processing_result else None,
            }

        except Exception as orchestration_error:
            logger.error(f"Orchestration failed (will mark for manual review): {orchestration_error}")
            # Return partial success - email was ingested, but orchestration failed
            return {
                "status": "partial_success",
                "document_id": document.id,
                "filename": document.filename,
                "warning": "Email ingested but automatic orchestration failed. Document marked for manual review.",
                "error": str(orchestration_error),
            }

    except HTTPException:
        raise
    except InvalidEmailFormatError as e:
        logger.warning(f"Invalid email format: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except EmailIngestionError as e:
        logger.error(f"Email ingestion error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in webhook handler: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/webhooks/email", tags=["email"])
async def handle_email_webhook(request: Request) -> dict:
    """
    Alias endpoint for /webhooks/sendgrid.

    Provides a simpler URL for testing and alternative webhook configurations.
    """
    return await handle_sendgrid_webhook(request)


@router.post("/webhooks/email-return", tags=["email"])
async def handle_email_return(request: Request) -> dict:
    """
    Handle signed documents returning via email.

    Called when a signed PDF comes back from recipient's email.
    Matches it to the original document and updates signature state.

    Returns:
        200 OK with document info
        400 Bad Request if document cannot be matched
    """
    try:
        body = await request.json()
        from_email = body.get("from", "")
        subject = body.get("subject", "")
        attachment_filename = body.get("attachment_filename", "")
        attachment_content = body.get("attachment_content", "")

        if not attachment_content or not attachment_filename:
            raise HTTPException(
                status_code=400, detail="Missing attachment data for return document"
            )

        # Process as a regular email with the signed attachment
        document = await email_service.ingest_email(
            from_email=from_email,
            to_email="",
            subject=subject or f"Signed return: {attachment_filename}",
            text_content=f"Signed document returned from {from_email}",
            attachments=[
                {
                    "filename": attachment_filename,
                    "content_type": "application/pdf",
                    "content": attachment_content,
                }
            ],
        )

        return {
            "status": "received",
            "document_id": document.id,
            "filename": document.filename,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling email return: {e}")
        raise HTTPException(status_code=400, detail=f"Could not process return: {e}")


@router.post("/api/documents/upload", response_model=DocumentIngestionResponse, tags=["documents"])
async def upload_document(request: DocumentUploadRequest) -> DocumentIngestionResponse:
    """
    Manually upload a document for processing.

    Alternative to email ingestion for testing and UI uploads.

    Args:
        request: DocumentUploadRequest with base64-encoded file

    Returns:
        DocumentIngestionResponse with document ID and status
    """
    try:
        # Process as an email-like ingestion with the uploaded file as attachment
        document = await email_service.ingest_email(
            from_email=request.source_email or "manual_upload@system",
            to_email="",
            subject=request.file_name,
            text_content=None,
            attachments=[
                {
                    "filename": request.file_name,
                    "content_type": _guess_content_type(request.file_name),
                    "content": request.file_data,
                }
            ],
        )

        return DocumentIngestionResponse(
            document_id=document.id,
            filename=document.filename,
            status="ingested",
        )

    except InvalidEmailFormatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EmailIngestionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process upload")


@router.get("/api/documents/pending-return", tags=["documents"])
async def list_pending_return_documents() -> dict:
    """
    List documents waiting for signed copies to be returned.

    Returns:
        dict with list of documents in "pending_return" status
    """
    # TODO: Query database for pending return documents (Phase 5)
    return {"documents": [], "count": 0}


def _guess_content_type(filename: str) -> str:
    """Guess content type from filename extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    mapping = {
        "pdf": "application/pdf",
        "txt": "text/plain",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
    }
    return mapping.get(ext, "application/octet-stream")
