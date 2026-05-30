"""Notification sending for Domain 3: Box Integration."""

from typing import List, Optional
import httpx
from backend.shared.config import Config
from backend.shared.errors import NotificationError
from backend.shared.logging import get_logger

logger = get_logger(__name__)


class NotificationManager:
    """Manages sending notifications via Slack, email, etc."""

    async def send_notifications(
        self,
        document_id: str,
        doc_type: str,
        assigned_to_email: str,
        channels: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
    ) -> List[str]:
        """Send notifications for processed document.

        Attempts to send to each requested channel. Failures on individual
        channels are logged but don't prevent other channels from being tried.

        Args:
            document_id: ID of processed document
            doc_type: Type of document
            assigned_to_email: Email of assigned reviewer
            channels: List of notification channels ["slack", "email"]
            metadata: Optional classification metadata used to enrich the
                Slack message (e.g. confidence, vendor, amount, box_file_id)

        Returns:
            List[str]: Channels successfully notified
        """
        channels = channels or ["slack"]
        notified = []

        for channel in channels:
            try:
                if channel == "slack":
                    success = await self._send_slack_notification(
                        document_id, doc_type, assigned_to_email, metadata=metadata
                    )
                    if success:
                        notified.append("slack")
                elif channel == "email":
                    success = await self._send_email_notification(
                        document_id, assigned_to_email
                    )
                    if success:
                        notified.append("email")
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
            except Exception as e:
                logger.error(
                    f"Failed to send {channel} notification for "
                    f"document {document_id}: {e}"
                )

        logger.info(
            f"Notifications sent for document {document_id}: {notified}"
        )
        return notified

    async def _send_slack_notification(
        self,
        document_id: str,
        doc_type: str,
        assigned_to_email: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """Send Slack notification via webhook.

        Args:
            document_id: Document ID
            doc_type: Document type
            assigned_to_email: Assigned reviewer email
            metadata: Optional classification metadata used to enrich the
                Slack message payload

        Returns:
            bool: True if successful
        """
        webhook_url = Config.SLACK_WEBHOOK_URL

        message = self._build_slack_message(
            document_id, doc_type, assigned_to_email, metadata
        )

        # In demo mode or if no webhook configured, simulate success
        if Config.DEMO_MODE or not webhook_url:
            logger.info(
                f"[DEMO] Slack payload for document {document_id}: {message}"
            )
            return True

        try:
            async with httpx.AsyncClient(timeout=Config.WEBHOOK_TIMEOUT_SEC) as client:
                response = await client.post(webhook_url, json=message)
                if response.status_code == 200:
                    logger.info(f"Slack notification sent for document {document_id}")
                    return True
                else:
                    logger.error(
                        f"Slack webhook returned {response.status_code}: "
                        f"{response.text}"
                    )
                    return False
        except httpx.TimeoutException:
            logger.error(f"Slack webhook timed out for document {document_id}")
            return False
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False

    async def _send_email_notification(
        self,
        document_id: str,
        assigned_to_email: str,
    ) -> bool:
        """Send email notification.

        In demo mode, simulates sending. In live mode, uses SendGrid.

        Args:
            document_id: Document ID
            assigned_to_email: Recipient email

        Returns:
            bool: True if successful
        """
        # In demo mode or if no API key configured, simulate success
        if Config.DEMO_MODE or not Config.SENDGRID_API_KEY:
            logger.info(
                f"[DEMO] Email notification sent to {assigned_to_email} "
                f"for document {document_id}"
            )
            return True

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=Config.SENDGRID_FROM_EMAIL,
                to_emails=assigned_to_email,
                subject=f"New Document for Review: {document_id}",
                html_content=(
                    f"<p>A new document has been assigned to you for review.</p>"
                    f"<p><strong>Document ID:</strong> {document_id}</p>"
                    f"<p>Please review the document in Box at your earliest convenience.</p>"
                ),
            )

            sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
            response = sg.send(message)

            if response.status_code in (200, 201, 202):
                logger.info(f"Email sent to {assigned_to_email} for document {document_id}")
                return True
            else:
                logger.error(f"SendGrid returned {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False

    @staticmethod
    def _format_percent(confidence) -> str:
        """Format a 0.0-1.0 confidence float as an integer percentage.

        Coerces via float() to tolerate ints or numeric strings.

        Args:
            confidence: Confidence value in the 0.0-1.0 range

        Returns:
            str: Percentage string, e.g. "96%"
        """
        return f"{round(float(confidence) * 100)}%"

    @staticmethod
    def _format_currency(amount) -> str:
        """Format a numeric amount as a currency value.

        Coerces via float() to tolerate ints or numeric strings.

        Args:
            amount: Numeric amount

        Returns:
            str: Currency string with thousands separators, e.g. "$15,500.00"
        """
        return f"${float(amount):,.2f}"

    def _build_slack_message(
        self,
        document_id: str,
        doc_type: str,
        assigned_to_email: str,
        metadata: Optional[dict] = None,
    ) -> dict:
        """Build Slack message payload.

        Args:
            document_id: Document ID
            doc_type: Document type
            assigned_to_email: Assigned reviewer
            metadata: Optional classification metadata. Recognised keys:
                ``confidence`` (0.0-1.0 float), ``vendor`` (str),
                ``amount`` (number), and ``box_file_id`` (str).

        Returns:
            dict: Slack message payload
        """
        meta = metadata or {}

        # Button URL: prefer box_file_id, fall back to document_id (Req 1.5, 1.6)
        box_file_id = meta.get("box_file_id") or document_id
        button_url = f"https://app.box.com/file/{box_file_id}"

        # Urgency decision (Req 1.7, 1.8)
        amount = meta.get("amount")
        is_urgent = doc_type == "invoice" and amount is not None and amount > 10000
        emoji = "🚨" if is_urgent else "📄"

        # Body lines: only include enrichment fields that are present (Req 1.2-1.4, 1.6)
        lines = [
            f"*New {doc_type.replace('_', ' ').title()} for Review*",
            f"Document ID: `{document_id}`",
            f"Assigned to: {assigned_to_email}",
        ]
        if "confidence" in meta:
            lines.append(f"Confidence: {self._format_percent(meta['confidence'])}")
        if "vendor" in meta:
            lines.append(f"Vendor: {meta['vendor']}")
        if "amount" in meta:
            lines.append(f"Amount: {self._format_currency(meta['amount'])}")

        button = {
            "type": "button",
            "text": {"type": "plain_text", "text": "Review in Box"},
            "url": button_url,
        }
        if is_urgent:
            button["style"] = "danger"  # Slack only honors primary/danger

        return {
            "text": f"{emoji} New {doc_type} document for review",
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "\n".join(lines)},
                },
                {
                    "type": "actions",
                    "elements": [button],
                },
            ],
        }
