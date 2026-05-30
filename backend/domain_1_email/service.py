"""Business logic for Domain 1: Email Ingestion."""

import base64
import hashlib
import hmac
import io
from typing import Optional

from backend.shared.config import Config
from backend.shared.errors import (
    AttachmentExtractionError,
    EmailIngestionError,
    InvalidEmailFormatError,
)
from backend.shared.logging import get_logger
from backend.shared.types import IngestedDocument
from .textract_parser import get_textract_parser

logger = get_logger(__name__)

# Maximum attachment size: 25 MB
MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024

# Supported attachment content types
SUPPORTED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "image/jpeg",
    "image/png",
}


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

        Extracts email content (preferring text over HTML), processes
        attachments (PDF text extraction, plain text decode), and returns
        a fully-populated IngestedDocument.

        Args:
            from_email: Sender email address
            to_email: Recipient email address
            subject: Email subject line
            text_content: Plain text email body
            html_content: HTML email body
            attachments: List of attachment dicts with filename, content (base64), content_type

        Returns:
            IngestedDocument with full text content

        Raises:
            InvalidEmailFormatError: If required fields are missing
            EmailIngestionError: If processing fails
        """
        if not from_email:
            raise InvalidEmailFormatError("Missing sender email address")
        if not subject and not text_content and not html_content and not attachments:
            raise InvalidEmailFormatError("Email has no content: no subject, body, or attachments")

        try:
            # 1. Extract email body — prefer plain text over HTML
            body_text = self._extract_body(text_content, html_content)

            # 2. Build combined content starting with subject + body
            content_parts = []
            if subject:
                content_parts.append(f"Subject: {subject}")
            if body_text:
                content_parts.append(body_text)

            # 3. Process attachments
            filename = subject or "email_document"
            content_type = "text/plain"
            file_size_bytes: Optional[int] = None

            if attachments and len(attachments) > 0:
                for attachment in attachments:
                    att_filename = attachment.get("filename", "attachment")
                    att_content_type = attachment.get("content_type", "application/octet-stream")
                    att_content_b64 = attachment.get("content", "")

                    # Decode base64 content
                    try:
                        raw_bytes = base64.b64decode(att_content_b64)
                    except Exception as e:
                        logger.warning(f"Failed to decode attachment {att_filename}: {e}")
                        content_parts.append(f"\n[Attachment: {att_filename} - could not decode]")
                        continue

                    # Validate size
                    if len(raw_bytes) > MAX_ATTACHMENT_SIZE_BYTES:
                        logger.warning(f"Attachment {att_filename} exceeds size limit")
                        content_parts.append(f"\n[Attachment: {att_filename} - exceeds size limit]")
                        continue

                    # Extract text from attachment
                    extracted_text = await self._extract_attachment_text(
                        raw_bytes, att_content_type, att_filename
                    )
                    if extracted_text:
                        content_parts.append(f"\n--- Attachment: {att_filename} ---\n{extracted_text}")

                    # Use first attachment's metadata for the document
                    if attachments.index(attachment) == 0:
                        filename = att_filename
                        if att_content_type in SUPPORTED_CONTENT_TYPES:
                            content_type = att_content_type
                        file_size_bytes = len(raw_bytes)

            # 4. Combine all content
            full_content = "\n".join(content_parts).strip()

            if not full_content:
                full_content = f"Subject: {subject}" if subject else "[Empty email]"

            # 5. Create and return IngestedDocument
            document = IngestedDocument(
                filename=filename,
                content=full_content,
                content_type=content_type,
                source="email",
                email_from=from_email,
                file_size_bytes=file_size_bytes,
            )

            logger.info(
                f"Ingested email from {from_email}: "
                f"filename={document.filename}, "
                f"content_type={document.content_type}, "
                f"content_length={len(document.content)}"
            )

            return document

        except (InvalidEmailFormatError, AttachmentExtractionError):
            raise
        except Exception as e:
            logger.error(f"Email ingestion failed: {e}")
            raise EmailIngestionError(f"Failed to ingest email: {e}") from e

    async def validate_sendgrid_signature(
        self, signature: str, timestamp: str, payload: str
    ) -> bool:
        """
        Validate SendGrid webhook signature using HMAC-SHA256.

        Args:
            signature: Signature from X-Twilio-Email-Event-Webhook-Signature header
            timestamp: Timestamp from X-Twilio-Email-Event-Webhook-Timestamp header
            payload: Raw request body

        Returns:
            bool: True if signature is valid, False otherwise
        """
        verify_token = Config.SENDGRID_VERIFY_TOKEN
        if not verify_token:
            # In development/demo mode, skip validation if no token configured
            logger.warning("No SENDGRID_VERIFY_TOKEN configured — skipping signature validation")
            return True

        try:
            # SendGrid signature: HMAC-SHA256(timestamp + payload, token)
            message = (timestamp + payload).encode("utf-8")
            key = verify_token.encode("utf-8")
            expected_signature = hmac.new(key, message, hashlib.sha256).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature validation error: {e}")
            return False

    def _extract_body(
        self, text_content: Optional[str], html_content: Optional[str]
    ) -> str:
        """
        Extract email body, preferring plain text over HTML.

        For HTML, does a basic strip of tags to get readable text.
        """
        if text_content and text_content.strip():
            return text_content.strip()

        if html_content and html_content.strip():
            return self._html_to_text(html_content)

        return ""

    def _html_to_text(self, html: str) -> str:
        """Basic HTML to text conversion — strips tags."""
        import re

        # Remove script and style blocks
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        # Replace <br> and <p> with newlines
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
        # Strip remaining tags
        text = re.sub(r"<[^>]+>", "", text)
        # Collapse whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    async def _extract_attachment_text(
        self, raw_bytes: bytes, content_type: str, filename: str
    ) -> str:
        """
        Extract text content from an attachment based on its content type.

        Supports:
        - text/plain: Direct decode
        - application/pdf: PDF text extraction via Amazon Textract (with pdfplumber/PyPDF2 fallback)
        - image/*: Placeholder (OCR not implemented for hackathon)

        Args:
            raw_bytes: Raw file bytes
            content_type: MIME type of the attachment
            filename: Original filename

        Returns:
            Extracted text content, or empty string if extraction fails
        """
        try:
            if content_type == "text/plain":
                return raw_bytes.decode("utf-8", errors="replace")

            if content_type == "application/pdf":
                return await self._extract_pdf_text(raw_bytes, filename)

            if content_type.startswith("image/"):
                # For hackathon: skip OCR, return placeholder
                logger.info(f"Image attachment {filename} — OCR not implemented")
                return f"[Image attachment: {filename}]"

            # Unsupported type
            logger.info(f"Unsupported attachment type {content_type} for {filename}")
            return f"[Attachment: {filename} ({content_type})]"

        except Exception as e:
            logger.warning(f"Failed to extract text from {filename}: {e}")
            return f"[Could not extract text from: {filename}]"

    async def _extract_pdf_text(self, raw_bytes: bytes, filename: str) -> str:
        """
        Extract text from PDF bytes.

        Priority order:
        1. Amazon Textract (if enabled and credentials available)
        2. pdfplumber (local, no dependencies)
        3. PyPDF2 (fallback)

        Args:
            raw_bytes: Raw PDF file bytes
            filename: Original filename

        Returns:
            Extracted text or placeholder string
        """
        # Try Amazon Textract first
        try:
            textract = get_textract_parser()
            if textract.enabled:
                logger.info(f"Using Amazon Textract for {filename}")
                text = await textract.extract_pdf_text(raw_bytes, filename)
                if text:
                    return text
        except Exception as e:
            logger.warning(f"Textract extraction failed for {filename}, falling back: {e}")

        # Fallback to pdfplumber
        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
                pages_text = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(page_text)
                if pages_text:
                    logger.info(f"Extracted {len(pages_text)} pages using pdfplumber from {filename}")
                    return "\n\n".join(pages_text)
        except ImportError:
            logger.debug("pdfplumber not available, trying PyPDF2")
        except Exception as e:
            logger.warning(f"pdfplumber failed for {filename}: {e}")

        # Final fallback to PyPDF2
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(io.BytesIO(raw_bytes))
            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            if pages_text:
                logger.info(f"Extracted {len(pages_text)} pages using PyPDF2 from {filename}")
                return "\n\n".join(pages_text)
        except ImportError:
            logger.warning("Neither pdfplumber nor PyPDF2 available for PDF extraction")
        except Exception as e:
            logger.warning(f"PyPDF2 failed for {filename}: {e}")

        return f"[Could not extract PDF text from: {filename}]"
