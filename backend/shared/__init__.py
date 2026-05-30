"""Shared utilities and types for Box Smart Inbox."""

from backend.shared.types import IngestedDocument, ClassificationResult, ProcessingResult
from backend.shared.config import Config
from backend.shared.errors import (
    BoxSmartInboxException,
    EmailIngestionError,
    ClassificationError,
    BoxIntegrationError,
)
from backend.shared.logging import setup_logging, get_logger

__all__ = [
    "IngestedDocument",
    "ClassificationResult",
    "ProcessingResult",
    "Config",
    "BoxSmartInboxException",
    "EmailIngestionError",
    "ClassificationError",
    "BoxIntegrationError",
    "setup_logging",
    "get_logger",
]
