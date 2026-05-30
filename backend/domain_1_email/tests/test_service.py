"""Tests for Domain 1 email service."""

import pytest
from backend.shared.fixtures import MOCK_INGESTED_DOCUMENT_EMAIL
from backend.domain_1_email.service import EmailIngestionService


@pytest.mark.domain1
class TestEmailIngestionService:
    """Tests for EmailIngestionService."""

    @pytest.fixture
    def service(self):
        """Create email service instance."""
        return EmailIngestionService()

    @pytest.mark.asyncio
    async def test_ingest_email_plain_text(self, service):
        """
        TODO: Test ingesting plain text email.

        1. Call service.ingest_email() with plain text email
        2. Assert returns IngestedDocument
        3. Assert content contains the email text
        4. Assert content_type is "text/plain"
        """
        raise NotImplementedError("TODO: Implement plain text email ingest test")

    @pytest.mark.asyncio
    async def test_ingest_email_with_attachment(self, service):
        """
        TODO: Test ingesting email with attachment.

        1. Create email with PDF attachment
        2. Call service.ingest_email()
        3. Assert IngestedDocument contains extracted content
        4. Assert filename matches attachment name
        """
        raise NotImplementedError("TODO: Implement email with attachment test")

    @pytest.mark.asyncio
    async def test_ingest_email_html_to_text(self, service):
        """
        TODO: Test ingesting HTML email converts to text.

        1. Create email with HTML body but no text body
        2. Call service.ingest_email()
        3. Assert HTML is converted to plain text
        """
        raise NotImplementedError("TODO: Implement HTML to text conversion test")

    def test_validate_sendgrid_signature_valid(self, service):
        """
        TODO: Test signature validation with valid signature.

        1. Generate valid signature using SendGrid algorithm
        2. Call service.validate_sendgrid_signature()
        3. Assert returns True
        """
        raise NotImplementedError("TODO: Implement signature validation test")

    def test_validate_sendgrid_signature_invalid(self, service):
        """
        TODO: Test signature validation with invalid signature.

        1. Use bad signature
        2. Call service.validate_sendgrid_signature()
        3. Assert returns False
        """
        raise NotImplementedError("TODO: Implement invalid signature test")
