"""Configuration management for Box Smart Inbox."""

import os
from typing import Literal
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    CEREBRAS = "cerebras"
    GROQ = "groq"
    GEMINI = "gemini"


class DocumentType(str, Enum):
    """Supported document types."""

    INVOICE = "invoice"
    CONTRACT = "contract"
    RESUME = "resume"
    RECEIPT = "receipt"
    ID_DOCUMENT = "id_document"
    PURCHASE_ORDER = "purchase_order"
    OTHER = "other"


class Config:
    """Application configuration loaded from environment variables."""

    # Application settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = ENVIRONMENT == "development"

    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Domain 1: Email Ingestion
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_VERIFY_TOKEN: str = os.getenv("SENDGRID_VERIFY_TOKEN", "")
    SENDGRID_INBOUND_URL: str = os.getenv("SENDGRID_INBOUND_URL", "")

    POSTMARK_API_KEY: str = os.getenv("POSTMARK_API_KEY", "")
    POSTMARK_INBOUND_URL: str = os.getenv("POSTMARK_INBOUND_URL", "")

    # Domain 2: AI Classification
    LLM_PROVIDER: LLMProvider = LLMProvider(os.getenv("LLM_PROVIDER", "cerebras"))
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Domain 3: Box Integration
    BOX_CLIENT_ID: str = os.getenv("BOX_CLIENT_ID", "")
    BOX_CLIENT_SECRET: str = os.getenv("BOX_CLIENT_SECRET", "")
    BOX_ENTERPRISE_ID: str = os.getenv("BOX_ENTERPRISE_ID", "")
    BOX_DEMO_FOLDER_ID: str = os.getenv("BOX_DEMO_FOLDER_ID", "0")

    # Notifications
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")

    # Webhooks
    WEBHOOK_PRIMARY_KEY: str = os.getenv("WEBHOOK_PRIMARY_KEY", "")
    WEBHOOK_SECONDARY_KEY: str = os.getenv("WEBHOOK_SECONDARY_KEY", "")

    # Redis (optional async queue)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    USE_ASYNC_QUEUE: bool = os.getenv("USE_ASYNC_QUEUE", "false").lower() == "true"

    # Demo mode (replay cached responses)
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() == "true"

    # Constants
    MAX_DOCUMENT_SIZE_MB: int = 25
    DOCUMENT_PROCESSING_TIMEOUT_SEC: int = 30
    WEBHOOK_TIMEOUT_SEC: int = 10

    @staticmethod
    def validate():
        """Validate required configuration is present."""
        required_keys = [
            "SENDGRID_API_KEY",
            "LLM_PROVIDER",
            "BOX_CLIENT_ID",
            "BOX_CLIENT_SECRET",
        ]

        missing = []
        for key in required_keys:
            if not getattr(Config, key, None):
                missing.append(key)

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return True


# Document type to folder mapping
FOLDER_MAPPING = {
    "invoice": "/Invoices",
    "contract": "/Contracts",
    "resume": "/Resumes",
    "receipt": "/Receipts",
    "id_document": "/ID Documents",
    "purchase_order": "/Purchase Orders",
    "other": "/Other Documents",
}

# Document type to reviewer mapping
REVIEWER_MAPPING = {
    "invoice": "finance",
    "contract": "legal",
    "resume": "hr",
    "receipt": "finance",
    "id_document": "hr",
    "purchase_order": "procurement",
    "other": None,
}
