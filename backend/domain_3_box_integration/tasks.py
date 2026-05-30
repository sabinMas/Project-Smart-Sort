"""Task management for Domain 3: Box Integration."""

from typing import Optional
from backend.shared.config import REVIEWER_MAPPING
from backend.shared.errors import TaskCreationError
from backend.shared.logging import get_logger

logger = get_logger(__name__)

# Reviewer role to email mapping (configurable per environment)
REVIEWER_EMAIL_MAPPING = {
    "finance": "finance@company.com",
    "legal": "legal@company.com",
    "hr": "hr@company.com",
    "procurement": "procurement@company.com",
}


class TaskManager:
    """Manages Box task creation and assignment."""

    def __init__(self, box_client):
        """Initialize task manager.

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
        """Create a review task for a document in Box.

        Maps doc_type to the appropriate reviewer, creates a task on the file,
        and assigns it to the reviewer.

        Args:
            file_id: Box file ID
            doc_type: Document type (invoice, contract, etc.)
            assigned_to_email: Email of assigned reviewer (optional, auto-mapped if None)
            due_date: Due date for task (ISO format, optional)

        Returns:
            str: Box task ID

        Raises:
            TaskCreationError: If task creation fails
        """
        try:
            # Determine reviewer
            reviewer_role = self._get_reviewer_for_doc_type(doc_type)
            reviewer_email = assigned_to_email or self._get_email_for_role(reviewer_role)

            # Build task message
            message = self._build_task_message(doc_type, reviewer_role)

            # Create task on file
            task_id = await self.box_client.create_task(
                file_id=file_id,
                message=message,
                due_at=due_date,
            )

            # Assign to reviewer if we have an email
            if reviewer_email:
                await self.box_client.assign_task_to_user(task_id, reviewer_email)

            logger.info(
                f"Created review task {task_id} for {doc_type} "
                f"on file {file_id}, assigned to {reviewer_email}"
            )
            return task_id

        except Exception as e:
            raise TaskCreationError(
                f"Failed to create review task for file {file_id}: {e}"
            )

    async def assign_task(
        self,
        task_id: str,
        assigned_to_email: str,
    ) -> bool:
        """Assign a task to a specific user.

        Args:
            task_id: Box task ID
            assigned_to_email: Email of user to assign to

        Returns:
            bool: True if successful

        Raises:
            TaskCreationError: If assignment fails
        """
        try:
            result = await self.box_client.assign_task_to_user(task_id, assigned_to_email)
            logger.info(f"Assigned task {task_id} to {assigned_to_email}")
            return result
        except Exception as e:
            raise TaskCreationError(
                f"Failed to assign task {task_id} to {assigned_to_email}: {e}"
            )

    def _get_reviewer_for_doc_type(self, doc_type: str) -> Optional[str]:
        """Get reviewer role for document type.

        Args:
            doc_type: Document type

        Returns:
            Optional[str]: Reviewer role or None
        """
        return REVIEWER_MAPPING.get(doc_type)

    def _get_email_for_role(self, role: Optional[str]) -> Optional[str]:
        """Get reviewer email for a role.

        Args:
            role: Reviewer role (finance, legal, hr, procurement)

        Returns:
            Optional[str]: Reviewer email or None
        """
        if role is None:
            return None
        return REVIEWER_EMAIL_MAPPING.get(role)

    def _build_task_message(self, doc_type: str, reviewer_role: Optional[str]) -> str:
        """Build a descriptive task message.

        Args:
            doc_type: Document type
            reviewer_role: Reviewer role

        Returns:
            str: Task message
        """
        role_display = reviewer_role.title() if reviewer_role else "General"
        return (
            f"Please review this {doc_type.replace('_', ' ')} document. "
            f"Assigned to {role_display} team for review and approval."
        )
