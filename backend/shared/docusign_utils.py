"""Utilities for DocuSign integration."""

from datetime import datetime, timedelta
from .config import Config


def calculate_signature_deadline() -> datetime:
    """Calculate signature deadline based on configured expiry days."""
    return datetime.utcnow() + timedelta(days=Config.DOCUSIGN_SIGNATURE_EXPIRY_DAYS)


def should_send_reminder(
    last_reminder_at: datetime,
    sent_at: datetime
) -> bool:
    """Check if reminder should be sent based on interval."""
    if not last_reminder_at:
        days_since_sent = (datetime.utcnow() - sent_at).days
        return days_since_sent >= Config.DOCUSIGN_REMINDER_INTERVAL_DAYS

    days_since_reminder = (datetime.utcnow() - last_reminder_at).days
    return days_since_reminder >= Config.DOCUSIGN_REMINDER_INTERVAL_DAYS


def get_days_until_expiry(expires_at: datetime) -> int:
    """Calculate days remaining until signature request expires."""
    days = (expires_at - datetime.utcnow()).days
    return max(0, days)


def should_send_final_notice(
    sent_at: datetime,
    expires_at: datetime
) -> bool:
    """Check if final notice should be sent (within 1 day of expiry)."""
    days_until_expiry = get_days_until_expiry(expires_at)
    return 0 <= days_until_expiry <= 1


def is_expired(expires_at: datetime) -> bool:
    """Check if signature request has expired."""
    return datetime.utcnow() > expires_at


def format_envelope_id(envelope_id: str) -> str:
    """Format and validate DocuSign envelope ID."""
    if not envelope_id or not isinstance(envelope_id, str):
        raise ValueError("Invalid envelope ID")
    return envelope_id.strip()
