"""Domain 1: Email Ingestion service."""

from backend.domain_1_email.service import EmailIngestionService
from backend.domain_1_email.routes import router

__all__ = ["EmailIngestionService", "router"]
