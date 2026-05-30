"""FastAPI routes for Domain 1: Email Ingestion."""

from fastapi import APIRouter, Request, HTTPException
from backend.domain_1_email.models import WebhookResponse
from backend.domain_1_email.service import EmailIngestionService
from backend.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/webhooks", tags=["email"])

email_service = EmailIngestionService()


@router.post("/email", response_model=WebhookResponse)
async def handle_email_webhook(request: Request) -> WebhookResponse:
    """
    Handle incoming email webhook from SendGrid or Postmark.

    TODO: Implement webhook handler:
    1. Validate webhook signature (use email_service.validate_sendgrid_signature)
    2. Parse email payload (from/to/subject/attachments)
    3. Call email_service.ingest_email() to process
    4. On success: Return {"status": "success", "document_id": "..."}
    5. On error: Log error and return 400 with error message

    The webhook will be called by SendGrid with multipart/form-data:
    - headers: Email headers
    - from: Sender email
    - to: Recipient email
    - subject: Subject line
    - text: Plain text body
    - html: HTML body
    - attachment files (multiple)

    Returns:
        WebhookResponse: Status and document ID

    Raises:
        HTTPException: If signature validation fails or processing errors occur
    """
    raise NotImplementedError("TODO: Implement SendGrid webhook handler")


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for Domain 1.

    Returns:
        dict: Status information
    """
    return {"status": "ok", "service": "email-ingestion"}
