"""Business logic for Domain 3: Box Integration."""

import io
import asyncio
from datetime import datetime, timezone
from typing import Optional
from backend.shared.types import ClassificationResult, ProcessingResult
from backend.shared.config import FOLDER_MAPPING, REVIEWER_MAPPING
from backend.shared.errors import BoxIntegrationError
from backend.shared.logging import get_logger
from backend.domain_3_box_integration.box_client import BoxClient
from backend.domain_3_box_integration.metadata import MetadataManager
from backend.domain_3_box_integration.tasks import TaskManager, REVIEWER_EMAIL_MAPPING
from backend.domain_3_box_integration.notifications import NotificationManager

logger = get_logger(__name__)


class BoxIntegrationService:
    """Service for integrating classified documents into Box.

    Orchestrates the full flow: folder routing, metadata application,
    task creation, and notification sending.
    """

    def __init__(self):
        """Initialize Box integration service with sub-managers."""
        self.box_client = BoxClient()
        self.metadata_manager = MetadataManager()
        self.task_manager = TaskManager(self.box_client)
        self.notification_manager = NotificationManager()

    async def process(
        self,
        classification_result: ClassificationResult,
        raw_file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
    ) -> ProcessingResult:
        """Process a classification result through Box integration.

        End-to-end flow:
        1. Get or create destination folder using FOLDER_MAPPING
        2. Move file to correct folder
        3. Apply metadata from classification
        4. Create review task with assigned reviewer
        5. Send notifications (Slack + Email)
        6. Return ProcessingResult with all details
        7. Handle errors gracefully (return failure instead of crashing)

        Args:
            classification_result: ClassificationResult from Domain 2

        Returns:
            ProcessingResult: Final processing result with status
        """
        document_id = classification_result.document_id
        doc_type = classification_result.doc_type

        logger.info(
            f"Processing document {document_id} "
            f"(type={doc_type}, confidence={classification_result.confidence})"
        )

        try:
            # Step 1: Route to destination folder
            folder_path = self._get_destination_path(doc_type)
            folder_id = await self.box_client.get_or_create_folder(folder_path)

            # Step 2: Upload file to correct Box folder
            # If we have raw bytes, upload them. Otherwise use document_id as reference.
            if raw_file_bytes:
                upload_filename = filename or f"{doc_type}_{document_id}.pdf"
                file_id = await self.box_client.upload_file_bytes(
                    file_bytes=raw_file_bytes,
                    folder_id=folder_id,
                    file_name=upload_filename,
                )
                logger.info(f"Uploaded file '{upload_filename}' to {folder_path}")
            else:
                # Fallback: try to move existing file (legacy path)
                file_id = await self._move_to_destination_folder(document_id, doc_type)

            # Step 3: Apply metadata
            metadata = await self._apply_metadata(file_id, classification_result)

            # Step 4: Create and assign review task
            task_id, reviewer_email = await self._create_and_assign_task(
                file_id, doc_type
            )

            # Step 5: Send notifications
            notified = await self.notification_manager.send_notifications(
                document_id=document_id,
                doc_type=doc_type,
                assigned_to_email=reviewer_email or "",
                channels=["slack", "email"],
            )

            result = ProcessingResult(
                document_id=document_id,
                box_file_id=file_id,
                destination_folder=folder_path,
                status="success",
                task_id=task_id,
                assigned_to=reviewer_email,
                metadata_applied=metadata,
                notification_sent_to=notified,
                error_message=None,
                completed_at=datetime.now(timezone.utc),
            )

            logger.info(
                f"Successfully processed document {document_id} -> "
                f"folder={folder_path}, task={task_id}, reviewer={reviewer_email}"
            )
            return result

        except Exception as e:
            logger.error(
                f"Failed to process document {document_id}: {e}",
                exc_info=True,
            )
            return ProcessingResult(
                document_id=document_id,
                box_file_id="",
                destination_folder="",
                status="failure",
                task_id=None,
                assigned_to=None,
                metadata_applied={},
                notification_sent_to=[],
                error_message=str(e),
                completed_at=datetime.now(timezone.utc),
            )

    def _get_destination_path(self, doc_type: str) -> str:
        """Get the destination folder path for a document type.

        Builds a path like "/Invoices/2024/May" for time-based routing,
        or just "/Resumes" for types that don't need date subfolders.

        Args:
            doc_type: Document type

        Returns:
            str: Folder path
        """
        base_path = FOLDER_MAPPING.get(doc_type, "/Other Documents")
        now = datetime.now(timezone.utc)

        # Add year/month subfolders for invoices, contracts, receipts, purchase_orders
        if doc_type in ("invoice", "contract", "receipt", "purchase_order"):
            return f"{base_path}/{now.year}/{now.strftime('%B')}"

        return base_path

    async def _move_to_destination_folder(
        self,
        file_id: str,
        doc_type: str,
    ) -> str:
        """Move file to destination folder based on document type.

        Args:
            file_id: Box file ID (or document_id as reference)
            doc_type: Document type

        Returns:
            str: The file ID after move

        Raises:
            BoxIntegrationError: If move fails
        """
        folder_path = self._get_destination_path(doc_type)
        folder_id = await self.box_client.get_or_create_folder(folder_path)
        moved_file_id = await self.box_client.move_file(file_id, folder_id)
        logger.info(f"Moved file {file_id} to {folder_path} (folder_id={folder_id})")
        return moved_file_id

    async def _apply_metadata(
        self,
        file_id: str,
        classification_result: ClassificationResult,
    ) -> dict:
        """Apply metadata to file in Box.

        Args:
            file_id: Box file ID
            classification_result: Classification data

        Returns:
            dict: Applied metadata
        """
        metadata = self.metadata_manager.build_metadata_dict(classification_result)
        await self.metadata_manager.apply_metadata(file_id, metadata)

        # Also apply via box_client for actual Box API metadata
        await self.box_client.apply_metadata(file_id, metadata)

        return metadata

    async def _create_and_assign_task(
        self,
        file_id: str,
        doc_type: str,
    ) -> tuple:
        """Create and assign review task.

        Args:
            file_id: Box file ID
            doc_type: Document type

        Returns:
            tuple: (task_id, assigned_to_email)
        """
        reviewer_role = REVIEWER_MAPPING.get(doc_type)
        reviewer_email = REVIEWER_EMAIL_MAPPING.get(reviewer_role) if reviewer_role else None

        task_id = await self.task_manager.create_review_task(
            file_id=file_id,
            doc_type=doc_type,
            assigned_to_email=reviewer_email,
        )

        return task_id, reviewer_email
