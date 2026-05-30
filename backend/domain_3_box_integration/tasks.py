"""Task management for Domain 3: Box Integration."""

from typing import Optional
from backend.shared.logging import get_logger

logger = get_logger(__name__)


class TaskManager:
    """Manages Box task creation and assignment."""

    def __init__(self, box_client):
        """
        Initialize task manager.

        Args:
            box_client: BoxClient instance
        """
        self.box_client = box_client

    async def create_review_task(
        self,
        file_id: str,
        doc_type: str,
        assigned_to_email: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> str:
        """
        Create a review task for a document in Box.

        TODO: Implement task creation:
        1. Map doc_type to appropriate reviewer (finance, legal, hr, procurement)
        2. If assigned_to_email not provided, use mapping
        3. Create Box task on file_id
        4. Set task message to describe review needed
        5. Assign to reviewer
        6. Return task ID

        Args:
            file_id: Box file ID
            doc_type: Document type (invoice, contract, etc.)
            assigned_to_email: Email of assigned reviewer (optional)
            due_date: Due date for task (ISO format, optional)

        Returns:
            str: Box task ID

        Raises:
            TaskCreationError: If task creation fails
        """
        raise NotImplementedError("TODO: Implement task creation")

    async def assign_task(
        self,
        task_id: str,
        assigned_to_email: str,
    ) -> bool:
        """
        Assign a task to a specific user.

        Args:
            task_id: Box task ID
            assigned_to_email: Email of user to assign to

        Returns:
            bool: True if successful

        Raises:
            TaskCreationError: If assignment fails
        """
        raise NotImplementedError("TODO: Implement task assignment")

    def _get_reviewer_for_doc_type(self, doc_type: str) -> Optional[str]:
        """
        Get reviewer email for document type.

        Maps document types to reviewer roles:
        - invoice -> finance
        - contract -> legal
        - resume -> hr
        - purchase_order -> procurement
        - etc.

        Args:
            doc_type: Document type

        Returns:
            Optional[str]: Reviewer role or None
        """
        reviewer_mapping = {
            "invoice": "finance",
            "contract": "legal",
            "resume": "hr",
            "receipt": "finance",
            "id_document": "hr",
            "purchase_order": "procurement",
            "other": None,
        }
        return reviewer_mapping.get(doc_type)
