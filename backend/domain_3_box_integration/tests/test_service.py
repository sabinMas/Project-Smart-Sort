"""Tests for Domain 3 Box integration service."""

import os
import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock

from backend.shared.types import ClassificationResult, ProcessingResult
from backend.shared.config import FOLDER_MAPPING, REVIEWER_MAPPING
from backend.shared.fixtures import (
    MOCK_CLASSIFICATION_INVOICE,
    MOCK_CLASSIFICATION_CONTRACT,
    MOCK_CLASSIFICATION_RESUME,
    MOCK_CLASSIFICATION_RECEIPT,
    MOCK_PROCESSING_SUCCESS,
)


@pytest.fixture(autouse=True)
def enable_demo_mode():
    """Ensure demo mode is enabled for all tests."""
    os.environ["DEMO_MODE"] = "true"
    yield
    os.environ.pop("DEMO_MODE", None)


@pytest.fixture
def service():
    """Create Box integration service instance in demo mode."""
    from backend.domain_3_box_integration.service import BoxIntegrationService

    return BoxIntegrationService()


@pytest.mark.domain3
class TestBoxIntegrationService:
    """Tests for BoxIntegrationService."""

    @pytest.mark.asyncio
    async def test_process_invoice_classification(self, service):
        """Test processing an invoice classification result."""
        result = await service.process(MOCK_CLASSIFICATION_INVOICE)

        assert isinstance(result, ProcessingResult)
        assert result.status == "success"
        assert result.document_id == "doc-invoice-001"
        assert result.box_file_id != ""
        assert "/Invoices" in result.destination_folder
        assert result.assigned_to == "finance@company.com"
        assert result.task_id is not None
        assert result.error_message is None

    @pytest.mark.asyncio
    async def test_process_contract_classification(self, service):
        """Test processing a contract classification result."""
        result = await service.process(MOCK_CLASSIFICATION_CONTRACT)

        assert result.status == "success"
        assert "/Contracts" in result.destination_folder
        assert result.assigned_to == "legal@company.com"
        assert result.document_id == "doc-contract-001"

    @pytest.mark.asyncio
    async def test_process_resume_classification(self, service):
        """Test processing a resume classification result."""
        result = await service.process(MOCK_CLASSIFICATION_RESUME)

        assert result.status == "success"
        assert "/Resumes" in result.destination_folder
        assert result.assigned_to == "hr@company.com"

    @pytest.mark.asyncio
    async def test_process_receipt_classification(self, service):
        """Test processing a receipt classification result."""
        result = await service.process(MOCK_CLASSIFICATION_RECEIPT)

        assert result.status == "success"
        assert "/Receipts" in result.destination_folder
        assert result.assigned_to == "finance@company.com"

    @pytest.mark.asyncio
    async def test_metadata_application(self, service):
        """Test metadata is correctly applied to file."""
        result = await service.process(MOCK_CLASSIFICATION_INVOICE)

        assert result.status == "success"
        assert "document_type" in result.metadata_applied
        assert result.metadata_applied["document_type"] == "invoice"
        assert "confidence" in result.metadata_applied
        assert result.metadata_applied["confidence"] == "0.98"
        assert "extracted_vendor" in result.metadata_applied
        assert result.metadata_applied["extracted_vendor"] == "ACME Corporation"

    @pytest.mark.asyncio
    async def test_task_creation_and_assignment(self, service):
        """Test task creation and assignment."""
        result = await service.process(MOCK_CLASSIFICATION_INVOICE)

        assert result.task_id is not None
        assert result.task_id.startswith("task_")
        assert result.assigned_to == "finance@company.com"

    @pytest.mark.asyncio
    async def test_notification_sending(self, service):
        """Test notifications are sent."""
        result = await service.process(MOCK_CLASSIFICATION_INVOICE)

        assert "slack" in result.notification_sent_to
        assert "email" in result.notification_sent_to

    @pytest.mark.asyncio
    async def test_error_handling_returns_failure(self, service):
        """Test error handling returns failure ProcessingResult."""
        # Create a classification with an invalid doc_type to trigger error
        # We'll patch the box_client to raise an error
        with patch.object(
            service.box_client, "get_or_create_folder", side_effect=Exception("Box API error")
        ):
            result = await service.process(MOCK_CLASSIFICATION_INVOICE)

        assert result.status == "failure"
        assert result.error_message is not None
        assert "Box API error" in result.error_message
        assert result.box_file_id == ""
        assert result.destination_folder == ""

    @pytest.mark.asyncio
    async def test_folder_routing_all_types(self, service):
        """Test that all document types route to correct folders."""
        type_to_folder = {
            "invoice": "/Invoices",
            "contract": "/Contracts",
            "resume": "/Resumes",
            "receipt": "/Receipts",
            "id_document": "/ID Documents",
            "purchase_order": "/Purchase Orders",
            "other": "/Other Documents",
        }

        for doc_type, expected_folder in type_to_folder.items():
            path = service._get_destination_path(doc_type)
            assert expected_folder in path, (
                f"Expected '{expected_folder}' in path for {doc_type}, got '{path}'"
            )

    @pytest.mark.asyncio
    async def test_date_subfolder_for_invoices(self, service):
        """Test that invoices get year/month subfolders."""
        path = service._get_destination_path("invoice")
        now = datetime.utcnow()

        assert f"/{now.year}/" in path
        assert now.strftime("%B") in path

    @pytest.mark.asyncio
    async def test_no_date_subfolder_for_resumes(self, service):
        """Test that resumes don't get date subfolders."""
        path = service._get_destination_path("resume")

        assert path == "/Resumes"

    @pytest.mark.asyncio
    async def test_completed_at_is_set(self, service):
        """Test that completed_at timestamp is set."""
        result = await service.process(MOCK_CLASSIFICATION_INVOICE)

        assert result.completed_at is not None
        assert isinstance(result.completed_at, datetime)


@pytest.mark.domain3
class TestMetadataManager:
    """Tests for MetadataManager."""

    def test_build_metadata_dict(self):
        """Test building metadata from classification result."""
        from backend.domain_3_box_integration.metadata import MetadataManager

        manager = MetadataManager()
        metadata = manager.build_metadata_dict(MOCK_CLASSIFICATION_INVOICE)

        assert metadata["document_type"] == "invoice"
        assert metadata["confidence"] == "0.98"
        assert metadata["extracted_vendor"] == "ACME Corporation"
        assert metadata["extracted_amount"] == "5000.0"
        assert "vendor:acme" in metadata["tags"]

    def test_validate_metadata_valid(self):
        """Test validation passes for valid metadata."""
        from backend.domain_3_box_integration.metadata import MetadataManager

        manager = MetadataManager()
        metadata = {"document_type": "invoice", "confidence": "0.98"}
        assert manager._validate_metadata(metadata) is True

    def test_validate_metadata_missing_field(self):
        """Test validation fails for missing required field."""
        from backend.domain_3_box_integration.metadata import MetadataManager

        manager = MetadataManager()
        with pytest.raises(ValueError, match="Missing required metadata field"):
            manager._validate_metadata({"document_type": "invoice"})

    def test_validate_metadata_invalid_confidence(self):
        """Test validation fails for out-of-range confidence."""
        from backend.domain_3_box_integration.metadata import MetadataManager

        manager = MetadataManager()
        with pytest.raises(ValueError, match="Confidence must be"):
            manager._validate_metadata({"document_type": "invoice", "confidence": "1.5"})


@pytest.mark.domain3
class TestTaskManager:
    """Tests for TaskManager."""

    @pytest.mark.asyncio
    async def test_create_review_task(self, service):
        """Test creating a review task."""
        from backend.domain_3_box_integration.tasks import TaskManager

        task_manager = TaskManager(service.box_client)
        task_id = await task_manager.create_review_task(
            file_id="file_123",
            doc_type="invoice",
            assigned_to_email="finance@company.com",
        )

        assert task_id is not None
        assert task_id.startswith("task_")

    @pytest.mark.asyncio
    async def test_reviewer_mapping(self):
        """Test reviewer role mapping."""
        from backend.domain_3_box_integration.tasks import TaskManager

        # Use a mock box_client
        mock_client = MagicMock()
        task_manager = TaskManager(mock_client)

        assert task_manager._get_reviewer_for_doc_type("invoice") == "finance"
        assert task_manager._get_reviewer_for_doc_type("contract") == "legal"
        assert task_manager._get_reviewer_for_doc_type("resume") == "hr"
        assert task_manager._get_reviewer_for_doc_type("purchase_order") == "procurement"
        assert task_manager._get_reviewer_for_doc_type("other") is None


@pytest.mark.domain3
class TestNotificationManager:
    """Tests for NotificationManager."""

    @pytest.mark.asyncio
    async def test_send_notifications_demo_mode(self):
        """Test notifications succeed in demo mode."""
        from backend.domain_3_box_integration.notifications import NotificationManager

        manager = NotificationManager()
        result = await manager.send_notifications(
            document_id="doc-001",
            doc_type="invoice",
            assigned_to_email="finance@company.com",
            channels=["slack", "email"],
        )

        assert "slack" in result
        assert "email" in result

    @pytest.mark.asyncio
    async def test_send_notifications_unknown_channel(self):
        """Test unknown channel is skipped gracefully."""
        from backend.domain_3_box_integration.notifications import NotificationManager

        manager = NotificationManager()
        result = await manager.send_notifications(
            document_id="doc-001",
            doc_type="invoice",
            assigned_to_email="finance@company.com",
            channels=["slack", "carrier_pigeon"],
        )

        assert "slack" in result
        assert "carrier_pigeon" not in result

    def test_build_slack_message(self):
        """Test Slack message payload structure."""
        from backend.domain_3_box_integration.notifications import NotificationManager

        manager = NotificationManager()
        message = manager._build_slack_message(
            document_id="doc-001",
            doc_type="invoice",
            assigned_to_email="finance@company.com",
        )

        assert "text" in message
        assert "blocks" in message
        assert "invoice" in message["text"].lower()


@pytest.mark.domain3
class TestBoxClient:
    """Tests for BoxClient in demo mode."""

    @pytest.mark.asyncio
    async def test_upload_file(self, service):
        """Test file upload returns a file ID."""
        file_id = await service.box_client.upload_file(
            file_path="/tmp/test.pdf",
            folder_id="folder_123",
            file_name="test.pdf",
        )
        assert file_id.startswith("file_")

    @pytest.mark.asyncio
    async def test_move_file(self, service):
        """Test file move returns the file ID."""
        result = await service.box_client.move_file("file_123", "folder_456")
        assert result == "file_123"

    @pytest.mark.asyncio
    async def test_get_or_create_folder(self, service):
        """Test folder creation returns a folder ID."""
        folder_id = await service.box_client.get_or_create_folder("/Invoices/2024/May")
        assert folder_id.startswith("folder_")

    @pytest.mark.asyncio
    async def test_get_or_create_folder_cached(self, service):
        """Test that same path returns same folder ID (cached)."""
        id1 = await service.box_client.get_or_create_folder("/Invoices/2024")
        id2 = await service.box_client.get_or_create_folder("/Invoices/2024")
        assert id1 == id2

    @pytest.mark.asyncio
    async def test_create_task(self, service):
        """Test task creation returns a task ID."""
        task_id = await service.box_client.create_task(
            file_id="file_123",
            message="Please review this document",
        )
        assert task_id.startswith("task_")

    @pytest.mark.asyncio
    async def test_list_files(self, service):
        """Test listing files returns empty list in demo mode."""
        files = await service.box_client.list_files("folder_123")
        assert isinstance(files, list)
