"""FastAPI application entry point for Box Smart Inbox."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.shared.config import Config
from backend.shared.logging import setup_logging
from backend.shared.types import IngestedDocument, ProcessingResult
from backend.domain_1_email.routes import router as email_router
from backend.domain_2_classifier.service import ClassificationService
from backend.domain_3_box_integration.service import BoxIntegrationService

# Setup logging
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Box Smart Inbox",
    description="AI-powered document intake, classification, and routing system",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include domain 1 routes
app.include_router(email_router)

# Initialize services
classification_service = ClassificationService()
box_service = BoxIntegrationService()

# Track processing state (in-memory for hackathon)
documents_processed = []


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "box-smart-inbox",
        "environment": Config.ENVIRONMENT,
    }


@app.post("/documents/intake", response_model=ProcessingResult)
async def intake_document(document: IngestedDocument) -> ProcessingResult:
    """
    End-to-end document processing orchestration.

    TODO: Implement orchestration:
    1. Receive IngestedDocument from Domain 1
    2. Call classification_service.classify(document) → ClassificationResult
    3. Call box_service.process(classification_result) → ProcessingResult
    4. Track document in documents_processed list
    5. Return ProcessingResult

    This is the only place where domains interact with each other.
    Domain 1 -> Domain 2 -> Domain 3 pipeline.

    Args:
        document: IngestedDocument from email webhook

    Returns:
        ProcessingResult: Final result with Box file ID, task, status

    Raises:
        HTTPException: If processing fails
    """
    raise NotImplementedError("TODO: Implement document intake orchestration")


@app.get("/status")
async def get_status() -> dict:
    """
    Get system status and processing statistics.

    Returns:
        dict: Status including documents processed, success rate, etc.
    """
    total = len(documents_processed)
    successful = sum(1 for d in documents_processed if d.get("status") == "success")
    success_rate = (successful / total * 100) if total > 0 else 0

    return {
        "status": "operational",
        "documents_processed": total,
        "success_rate": f"{success_rate:.1f}%",
        "recent_documents": documents_processed[-10:] if documents_processed else [],
    }


@app.get("/documents/{document_id}")
async def get_document_status(document_id: str) -> dict:
    """
    Get status of a specific document through the pipeline.

    Args:
        document_id: ID of document to check

    Returns:
        dict: Document processing status

    Raises:
        HTTPException: If document not found
    """
    for doc in documents_processed:
        if doc.get("document_id") == document_id:
            return doc

    raise HTTPException(status_code=404, detail=f"Document {document_id} not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        log_level=Config.LOG_LEVEL.lower(),
    )
