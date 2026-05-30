"""Business logic for Domain 3: Box Integration."""

from backend.shared.types import ClassificationResult, ProcessingResult
from backend.shared.config import FOLDER_MAPPING, REVIEWER_MAPPING
from backend.shared.logging import get_logger
from backend.domain_3_box_integration.box_client import BoxClient
from backend.domain_3_box_integration.metadata import MetadataManager
from backend.domain_3_box_integration.tasks import TaskManager
from backend.domain_3_box_integration.notifications import NotificationManager

logger = get_logger(__name__)


class BoxIntegrationService:
    """Service for integrating classified documents into Box."""

    def __init__(self):
        """Initialize Box integration service with sub-managers."""
        self.box_client = BoxClient()
        self.metadata_manager = MetadataManager()
        self.task_manager = TaskManager(self.box_client)
        self.notification_manager = NotificationManager()

    async def process(self, classification_result: ClassificationResult) -> ProcessingResult:
        """
        Process a classification result through Box integration.

        TODO: Implement end-to-end processing:
        1. Get or create destination folder using FOLDER_MAPPING
        2. Move file to correct folder
        3. Apply metadata from classification
        4. Create review task with assigned reviewer
        5. Send notifications (Slack + Email)
        6. Return ProcessingResult with all details
        7. Handle errors gracefully (escalate if needed)

        Args:
            classification_result: ClassificationResult from Domain 2

        Returns:
            ProcessingResult: Final processing result with status

        Raises:
            BoxIntegrationError: If any step fails (caught and returned as failure)
        """
        raise NotImplementedError("TODO: Implement end-to-end Box processing")

    async def _move_to_destination_folder(
        self,
        file_id: str,
        doc_type: str,
    ) -> str:
        """
        Move file to destination folder based on document type.

        TODO: Implement folder routing:
        1. Use FOLDER_MAPPING to get folder path
        2. Create folder structure if needed
        3. Move file there
        4. Return destination folder path

        Args:
            file_id: Box file ID
            doc_type: Document type

        Returns:
            str: Destination folder path

        Raises:
            BoxIntegrationError: If move fails
        """
        raise NotImplementedError("TODO: Implement file move to destination")

    async def _apply_metadata(
        self,
        file_id: str,
        classification_result: ClassificationResult,
    ) -> dict:
        """
        Apply metadata to file in Box.

        Args:
            file_id: Box file ID
            classification_result: Classification data

        Returns:
            dict: Applied metadata

        Raises:
            MetadataApplicationError: If application fails
        """
        metadata = self.metadata_manager.build_metadata_dict(classification_result)
        await self.metadata_manager.apply_metadata(file_id, metadata)
        return metadata

    async def _create_and_assign_task(
        self,
        file_id: str,
        doc_type: str,
    ) -> tuple:
        """
        Create and assign review task.

        Args:
            file_id: Box file ID
            doc_type: Document type

        Returns:
            tuple: (task_id, assigned_to_email)

        Raises:
            TaskCreationError: If task creation fails
        """
        reviewer = REVIEWER_MAPPING.get(doc_type)
        task_id = await self.task_manager.create_review_task(
            file_id, doc_type, assigned_to_email=None
        )
        return task_id, reviewer
