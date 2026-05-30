"""Notification sending for Domain 3: Box Integration."""

from typing import List, Optional
from backend.shared.config import Config
from backend.shared.logging import get_logger

logger = get_logger(__name__)


class NotificationManager:
    """Manages sending notifications via Slack, email, etc."""

    async def send_notifications(
        self,
        document_id: str,
        doc_type: str,
        assigned_to_email: str,
        channels: List[str] = None,
    ) -> List[str]:
        """
        Send notifications for processed document.

        TODO: Implement notification logic:
        1. If "slack" in channels: Send to Slack webhook
        2. If "email" in channels: Send email notification
        3. Include document type, assigned reviewer, etc.
        4. Return list of channels successfully notified

        Args:
            document_id: ID of processed document
            doc_type: Type of document
            assigned_to_email: Email of assigned reviewer
            channels: List of notification channels ["slack", "email"]

        Returns:
            List[str]: Channels successfully notified

        Raises:
            NotificationError: If sending fails
        """
        channels = channels or ["slack"]
        notified = []

        if "slack" in channels:
            await self._send_slack_notification(document_id, doc_type, assigned_to_email)
            notified.append("slack")

        if "email" in channels:
            await self._send_email_notification(document_id, assigned_to_email)
            notified.append("email")

        return notified

    async def _send_slack_notification(
        self,
        document_id: str,
        doc_type: str,
        assigned_to_email: str,
    ) -> bool:
        """
        TODO: Send Slack notification.

        1. Use Config.SLACK_WEBHOOK_URL
        2. Format message with document info
        3. POST to webhook
        4. Handle errors gracefully

        Args:
            document_id: Document ID
            doc_type: Document type
            assigned_to_email: Assigned reviewer email

        Returns:
            bool: True if successful
        """
        raise NotImplementedError("TODO: Implement Slack notification")

    async def _send_email_notification(
        self,
        document_id: str,
        assigned_to_email: str,
    ) -> bool:
        """
        TODO: Send email notification.

        1. Compose email with document review link
        2. Send via SMTP or SendGrid
        3. Include Box link and due date

        Args:
            document_id: Document ID
            assigned_to_email: Recipient email

        Returns:
            bool: True if successful
        """
        raise NotImplementedError("TODO: Implement email notification")

    def _build_slack_message(
        self,
        document_id: str,
        doc_type: str,
        assigned_to_email: str,
    ) -> dict:
        """
        Build Slack message payload.

        Args:
            document_id: Document ID
            doc_type: Document type
            assigned_to_email: Assigned reviewer

        Returns:
            dict: Slack message payload
        """
        return {
            "text": f"📄 New document for review",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New {doc_type.title()} for Review*\n"
                        f"Document ID: {document_id}\n"
                        f"Assigned to: {assigned_to_email}",
                    },
                },
            ],
        }
