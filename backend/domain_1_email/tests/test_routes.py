"""Tests for Domain 1 email routes."""

import base64
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.mark.domain1
class TestEmailRoutes:
    """Tests for email webhook routes."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_health_check(self, client):
        """Test /health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_email_webhook_success(self, client):
        """Test successful email webhook processing via JSON."""
        payload = {
            "from": "test@acme.com",
            "to": "inbox@company.com",
            "subject": "Test Invoice #12345",
            "text": "Invoice from Acme Corp for $5000",
            "attachments": [],
        }

        response = client.post("/webhooks/email", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "document_id" in data
        # document_id should be a valid UUID format
        assert len(data["document_id"]) > 0

    def test_email_webhook_with_attachment(self, client):
        """Test email webhook with a text attachment."""
        attachment_content = base64.b64encode(b"Invoice details here").decode()

        payload = {
            "from": "vendor@supplier.com",
            "to": "inbox@company.com",
            "subject": "Invoice Attached",
            "text": "Please see attached.",
            "attachments": [
                {
                    "filename": "invoice.txt",
                    "content_type": "text/plain",
                    "content": attachment_content,
                }
            ],
        }

        response = client.post("/webhooks/email", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert data["filename"] == "invoice.txt"

    def test_email_webhook_invalid_payload(self, client):
        """Test webhook with missing required fields returns 400."""
        payload = {
            "from": "",
            "to": "",
            "subject": "",
            "text": None,
        }

        response = client.post("/webhooks/email", json=payload)
        assert response.status_code == 400

    def test_email_webhook_sendgrid_alias(self, client):
        """Test /webhooks/sendgrid endpoint works the same as /webhooks/email."""
        payload = {
            "from": "test@example.com",
            "to": "inbox@company.com",
            "subject": "Test via SendGrid endpoint",
            "text": "Testing the sendgrid route",
        }

        response = client.post("/webhooks/sendgrid", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_upload_document(self, client):
        """Test manual document upload endpoint."""
        file_content = base64.b64encode(b"Document content for upload").decode()

        payload = {
            "file_data": file_content,
            "file_name": "test_document.txt",
            "source": "manual_upload",
        }

        response = client.post("/api/documents/upload", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["document_id"]
        assert data["filename"] == "test_document.txt"
        assert data["status"] == "ingested"

    def test_pending_return_documents(self, client):
        """Test pending return documents endpoint."""
        response = client.get("/api/documents/pending-return")
        assert response.status_code == 200

        data = response.json()
        assert "documents" in data
        assert data["count"] == 0
