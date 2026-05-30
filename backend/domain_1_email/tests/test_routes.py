"""Tests for Domain 1 email routes."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.domain1
class TestEmailRoutes:
    """Tests for email webhook routes."""

    def test_health_check(self):
        """
        TODO: Test /webhooks/email health endpoint.

        Should return 200 with {"status": "ok"}
        """
        raise NotImplementedError("TODO: Implement health check test")

    def test_email_webhook_success(self):
        """
        TODO: Test successful email webhook processing.

        1. Create mock SendGrid email payload
        2. POST to /webhooks/email
        3. Assert 200 response with document_id
        4. Assert document_id is valid UUID format
        """
        raise NotImplementedError("TODO: Implement email webhook success test")

    def test_email_webhook_invalid_signature(self):
        """
        TODO: Test webhook with invalid signature.

        1. Create payload with bad signature
        2. POST to /webhooks/email
        3. Assert 400 or 401 response
        """
        raise NotImplementedError("TODO: Implement invalid signature test")

    def test_email_with_pdf_attachment(self):
        """
        TODO: Test email with PDF attachment.

        1. Create email with PDF file
        2. Call webhook
        3. Assert IngestedDocument has content extracted from PDF
        """
        raise NotImplementedError("TODO: Implement PDF attachment test")

    def test_email_with_multiple_attachments(self):
        """
        TODO: Test email with multiple attachments.

        1. Create email with 2+ attachments
        2. Call webhook
        3. Assert all attachments are extracted
        """
        raise NotImplementedError("TODO: Implement multiple attachments test")
