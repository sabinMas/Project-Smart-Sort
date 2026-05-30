"""Utilities for contact handling and verification."""

import re
from typing import List, Tuple

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)


def extract_emails_from_text(text: str) -> List[str]:
    """Extract email addresses from text."""
    if not text:
        return []
    matches = EMAIL_REGEX.findall(text)
    return list(set(matches))


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    if not email or len(email) > 254:
        return False
    return bool(EMAIL_REGEX.fullmatch(email))


def get_domain_from_email(email: str) -> str:
    """Extract domain from email address."""
    if "@" not in email:
        return ""
    return email.split("@")[1].lower()


def normalize_email(email: str) -> str:
    """Normalize email to lowercase and remove whitespace."""
    return email.strip().lower()


def deduplicate_emails(emails: List[str]) -> List[str]:
    """Remove duplicate emails (case-insensitive)."""
    seen = set()
    result = []
    for email in emails:
        normalized = normalize_email(email)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def calculate_verification_score(
    doc_confidence: float = 0.0,
    db_verified: bool = False,
    email_header_match: bool = False
) -> int:
    """
    Calculate composite verification score (0-100).
    Weights: document (40%), contact_db (40%), email_header (20%)
    """
    score = 0

    if doc_confidence > 0:
        score += int(doc_confidence * 40)

    if db_verified:
        score += 40

    if email_header_match:
        score += 20

    return min(100, max(0, score))


def parse_email_address(email_str: str) -> Tuple[str, str]:
    """
    Parse email string to name and email parts.
    Handles formats like:
    - "john@example.com"
    - "John Smith <john@example.com>"
    - "john@example.com (John Smith)"
    Returns: (name, email)
    """
    email_str = email_str.strip()

    if "<" in email_str:
        name = email_str.split("<")[0].strip()
        email = email_str.split("<")[1].rstrip(">").strip()
        return (name, email)

    if "(" in email_str:
        email = email_str.split("(")[0].strip()
        name = email_str.split("(")[1].rstrip(")").strip()
        return (name, email)

    return ("", email_str)
