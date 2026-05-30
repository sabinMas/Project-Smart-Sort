"""Tests for Domain 3 routes (Approvals, Signatures & Orchestration)."""

import os
import pytest
from unittest.mock import patch

# Ensure demo mode before importing anything
os.environ["DEMO_MODE"] = "true"
os.environ["ENVIRONMENT"] = "testing"


@pytest.fixture(autouse=True)
def enable_demo_mode():
    """Ensure demo mode is enabled and reset state between tests."""
    os.environ["DEMO_MODE"] = "true"
    # Reset in-memory stores
    from backend.domain_3_box_integration import approval_service
    approval_service._demo_documents.clear()
    approval_service._demo_approvals.clear()
    approval_service._demo_signature_states.clear()
    yield


@pytest.fixture
def approval_service_instance():
    """Create ApprovalService instance."""
    from backend.domain_3_box_integration.approval_service import ApprovalService
    return ApprovalService()


@pytest.fixture
def signature_service_instance():
    """Create SignatureService instance."""
    from backend.domain_3_box_integration.approval_service import SignatureService
    return SignatureService()


@pytest.fixture
def document_service_instance():
    """Create DocumentService instance."""
    from backend.domain_3_box_integration.approval_service import DocumentService
    return DocumentService()


@pytest.mark.domain3
class TestApprovalService:
    """Tests for ApprovalService."""

    @pytest.mark.asyncio
    async def test_approve_document(self, approval_service_instance):
        """Test approving a document."""
        result = await approval_service_instance.review_document(
            document_id="doc-001",
            action="approve",
            final_recipients=["alice@company.com", "bob@company.com"],
            reason="Looks good",
        )

        assert result["status"] == "approved"
        assert result["next_step"] == "ready_to_send_signature_request"
        assert result["approval_id"] is not None
        assert result["document_id"] == "doc-001"

    @pytest.mark.asyncio
    async def test_reject_document(self, approval_service_instance):
        """Test rejecting a document."""
        result = await approval_service_instance.review_document(
            document_id="doc-002",
            action="reject",
            final_recipients=["alice@company.com"],
            reason="Invalid document",
        )

        assert result["status"] == "rejected"
        assert result["next_step"] == "document_rejected"

    @pytest.mark.asyncio
    async def test_flag_for_review(self, approval_service_instance):
        """Test flagging a document for review."""
        result = await approval_service_instance.review_document(
            document_id="doc-003",
            action="flag_for_review",
            final_recipients=["alice@company.com"],
            reason="Needs manager approval",
        )

        assert result["status"] == "flagged"
        assert result["next_step"] == "manual_review_required"

    @pytest.mark.asyncio
    async def test_edit_recipients(self, approval_service_instance):
        """Test editing recipients."""
        result = await approval_service_instance.review_document(
            document_id="doc-004",
            action="edit",
            final_recipients=["alice@company.com", "manager@company.com"],
            changes_made=["Removed bob@, added manager@"],
        )

        assert result["status"] == "approved"
        assert result["next_step"] == "ready_to_send_signature_request"

    @pytest.mark.asyncio
    async def test_get_approval_history(self, approval_service_instance):
        """Test getting approval history."""
        # Create some approvals first
        await approval_service_instance.review_document(
            document_id="doc-005",
            action="approve",
            final_recipients=["alice@company.com"],
        )
        await approval_service_instance.review_document(
            document_id="doc-005",
            action="edit",
            final_recipients=["alice@company.com", "bob@company.com"],
            changes_made=["Added bob@"],
        )

        history = await approval_service_instance.get_approval_history("doc-005")
        assert len(history) == 2
        assert history[0]["action"] == "approve"
        assert history[1]["action"] == "edit"

    @pytest.mark.asyncio
    async def test_get_approval_history_empty(self, approval_service_instance):
        """Test getting approval history for document with no approvals."""
        history = await approval_service_instance.get_approval_history("doc-nonexistent")
        assert history == []


@pytest.mark.domain3
class TestSignatureService:
    """Tests for SignatureService."""

    @pytest.mark.asyncio
    async def test_send_for_signature(self, signature_service_instance):
        """Test sending document for signature."""
        result = await signature_service_instance.send_for_signature(
            document_id="doc-001",
            recipients=[
                {"email": "alice@company.com", "name": "Alice", "role": "signer"},
                {"email": "bob@company.com", "name": "Bob", "role": "signer"},
            ],
        )

        assert result["status"] == "sent"
        assert result["recipients_sent_to"] == 2
        assert result["docusign_envelope_id"].startswith("envelope_")
        assert result["expires_at"] is not None

    @pytest.mark.asyncio
    async def test_get_signature_status(self, signature_service_instance):
        """Test getting signature status after sending."""
        await signature_service_instance.send_for_signature(
            document_id="doc-001",
            recipients=[
                {"email": "alice@company.com", "name": "Alice", "role": "signer"},
            ],
        )

        status = await signature_service_instance.get_signature_status("doc-001")
        assert status["status"] == "awaiting_signatures"
        assert status["signed_count"] == 0
        assert status["total_count"] == 1
        assert status["completion_percentage"] == 0
        assert len(status["recipients"]) == 1

    @pytest.mark.asyncio
    async def test_get_signature_status_not_found(self, signature_service_instance):
        """Test getting status for document with no signature state."""
        status = await signature_service_instance.get_signature_status("doc-nonexistent")
        assert status["status"] == "not_found"

    @pytest.mark.asyncio
    async def test_docusign_webhook_recipient_completed(self, signature_service_instance):
        """Test handling recipient-completed webhook."""
        # First send for signature
        send_result = await signature_service_instance.send_for_signature(
            document_id="doc-001",
            recipients=[
                {"email": "alice@company.com", "name": "Alice", "role": "signer"},
                {"email": "bob@company.com", "name": "Bob", "role": "signer"},
            ],
        )

        envelope_id = send_result["docusign_envelope_id"]

        # Simulate recipient completing
        result = await signature_service_instance.handle_docusign_webhook(
            event="recipient-completed",
            data={
                "envelopeId": envelope_id,
                "recipientEmail": "alice@company.com",
                "status": "completed",
                "signedDateTime": "2024-05-30T10:15:00Z",
            },
        )

        assert result["status"] == "processed"

        # Check status updated
        status = await signature_service_instance.get_signature_status("doc-001")
        assert status["signed_count"] == 1
        assert status["total_count"] == 2
        assert status["completion_percentage"] == 50

    @pytest.mark.asyncio
    async def test_docusign_webhook_envelope_completed(self, signature_service_instance):
        """Test handling envelope-completed webhook (all signed)."""
        send_result = await signature_service_instance.send_for_signature(
            document_id="doc-001",
            recipients=[
                {"email": "alice@company.com", "name": "Alice", "role": "signer"},
            ],
        )

        envelope_id = send_result["docusign_envelope_id"]

        result = await signature_service_instance.handle_docusign_webhook(
            event="envelope-completed",
            data={"envelopeId": envelope_id},
        )

        assert result["status"] == "processed"

        status = await signature_service_instance.get_signature_status("doc-001")
        assert status["status"] == "complete"
        assert status["signed_count"] == status["total_count"]

    @pytest.mark.asyncio
    async def test_docusign_webhook_unknown_envelope(self, signature_service_instance):
        """Test webhook with unknown envelope ID."""
        result = await signature_service_instance.handle_docusign_webhook(
            event="recipient-completed",
            data={"envelopeId": "unknown_envelope", "recipientEmail": "x@y.com"},
        )

        assert result["status"] == "ignored"
        assert result["reason"] == "envelope_not_found"

    @pytest.mark.asyncio
    async def test_docusign_webhook_recipient_declined(self, signature_service_instance):
        """Test handling recipient-declined webhook."""
        send_result = await signature_service_instance.send_for_signature(
            document_id="doc-001",
            recipients=[
                {"email": "alice@company.com", "name": "Alice", "role": "signer"},
            ],
        )

        envelope_id = send_result["docusign_envelope_id"]

        result = await signature_service_instance.handle_docusign_webhook(
            event="recipient-declined",
            data={"envelopeId": envelope_id, "recipientEmail": "alice@company.com"},
        )

        assert result["status"] == "processed"

        status = await signature_service_instance.get_signature_status("doc-001")
        assert status["recipients"][0]["status"] == "declined"


@pytest.mark.domain3
class TestDocumentService:
    """Tests for DocumentService."""

    @pytest.mark.asyncio
    async def test_get_document_status_default(self, document_service_instance):
        """Test getting status for any document in demo mode."""
        result = await document_service_instance.get_document_status("doc-001")
        assert result is not None
        assert result["document_id"] == "doc-001"
        assert result["status"] == "classified"

    @pytest.mark.asyncio
    async def test_get_document_status_after_approval(
        self, document_service_instance, approval_service_instance
    ):
        """Test document status reflects approval."""
        await approval_service_instance.review_document(
            document_id="doc-001",
            action="approve",
            final_recipients=["alice@company.com"],
        )

        result = await document_service_instance.get_document_status("doc-001")
        assert result["status"] == "approved"

    @pytest.mark.asyncio
    async def test_list_documents_empty(self, document_service_instance):
        """Test listing documents when none exist."""
        result = await document_service_instance.list_documents()
        assert result["documents"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_list_documents_with_data(
        self, document_service_instance, approval_service_instance
    ):
        """Test listing documents after creating some."""
        await approval_service_instance.review_document(
            document_id="doc-001",
            action="approve",
            final_recipients=["alice@company.com"],
        )
        await approval_service_instance.review_document(
            document_id="doc-002",
            action="reject",
            final_recipients=["bob@company.com"],
        )

        result = await document_service_instance.list_documents()
        assert result["total"] == 2

    @pytest.mark.asyncio
    async def test_list_documents_filter_by_status(
        self, document_service_instance, approval_service_instance
    ):
        """Test filtering documents by status."""
        await approval_service_instance.review_document(
            document_id="doc-001",
            action="approve",
            final_recipients=["alice@company.com"],
        )
        await approval_service_instance.review_document(
            document_id="doc-002",
            action="reject",
            final_recipients=["bob@company.com"],
        )

        result = await document_service_instance.list_documents(status="approved")
        assert result["total"] == 1
        assert result["documents"][0]["document_id"] == "doc-001"
