"""Business logic for Domain 1: Email Ingestion."""

from typing import Optional
from backend.shared.types import IngestedDocument
from backend.shared.logging import get_logger

logger = get_logger(__name__)


class EmailIngestionService:
    """Service for handling email ingestion and document extraction."""

    async def ingest_email(
        self,
        from_email: str,
        to_email: str,
        subject: str,
        text_content: Optional[str] = None,
        html_content: Optional[str] = None,
        attachments: Optional[list] = None,
    ) -> IngestedDocument:
        """
        Process an incoming email and return an IngestedDocument.

        TODO: Implement email parsing logic:
        1. Extract email content (prefer text over HTML)
        2. For attachments:
           - Validate file type and size
           - Extract file content
           - For PDFs/images: Consider OCR if needed
        3. Create IngestedDocument with:
           - filename from subject or attachment name
           - content as full text + extracted attachment content
           - content_type based on attachment (pdf, image, text, etc.)
           - source="email"
           - email_from from sender
        4. Return IngestedDocument object

        Args:
            from_email: Sender email address
            to_email: Recipient email address
            subject: Email subject line
            text_content: Plain text email body
            html_content: HTML email body
            attachments: List of attachment metadata

        Returns:
            IngestedDocument: The ingested document object

        Raises:
            EmailIngestionError: If email processing fails
        """
        raise NotImplementedError("TODO: Implement email ingestion logic")

    async def validate_sendgrid_signature(self, signature: str, timestamp: str, payload: str) -> bool:
        """
        Validate SendGrid webhook signature.

        TODO: Implement signature validation:
        1. Use SENDGRID_VERIFY_TOKEN from config
        2. Combine timestamp + payload + token
        3. Generate HMAC-SHA256 hash
        4. Compare with provided signature

        Args:
            signature: Signature from X-Twilio-Email-Event-Webhook-Signature header
            timestamp: Timestamp from X-Twilio-Email-Event-Webhook-Timestamp header
            payload: Raw request body

        Returns:
            bool: True if signature is valid, False otherwise
        """
        raise NotImplementedError("TODO: Implement signature validation")
