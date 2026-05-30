"""Custom exceptions for Box Smart Inbox."""


class BoxSmartInboxException(Exception):
    """Base exception for all Box Smart Inbox errors."""

    pass


# Domain 1: Email Ingestion Errors
class EmailIngestionError(BoxSmartInboxException):
    """Base class for email ingestion errors."""

    pass


class InvalidEmailFormatError(EmailIngestionError):
    """Email format is invalid or missing required fields."""

    pass


class AttachmentExtractionError(EmailIngestionError):
    """Failed to extract attachments from email."""

    pass


class BoxUploadError(EmailIngestionError):
    """Failed to upload document to Box."""

    pass


# Domain 2: AI Classification Errors
class ClassificationError(BoxSmartInboxException):
    """Base class for classification errors."""

    pass


class LLMProviderError(ClassificationError):
    """Error communicating with LLM provider."""

    pass


class InvalidClassificationResultError(ClassificationError):
    """LLM returned invalid or malformed classification result."""

    pass


class ConfidenceScoreError(ClassificationError):
    """Confidence score is outside valid range [0.0, 1.0]."""

    pass


# Domain 3: Box Integration Errors
class BoxIntegrationError(BoxSmartInboxException):
    """Base class for Box integration errors."""

    pass


class BoxAuthenticationError(BoxIntegrationError):
    """Failed to authenticate with Box API."""

    pass


class BoxFileNotFoundError(BoxIntegrationError):
    """File not found in Box."""

    pass


class MetadataApplicationError(BoxIntegrationError):
    """Failed to apply metadata to file in Box."""

    pass


class TaskCreationError(BoxIntegrationError):
    """Failed to create task in Box."""

    pass


class NotificationError(BoxIntegrationError):
    """Failed to send notification (Slack, email, etc.)."""

    pass


# Configuration Errors
class ConfigurationError(BoxSmartInboxException):
    """Configuration is missing or invalid."""

    pass


class MissingEnvironmentVariableError(ConfigurationError):
    """Required environment variable is missing."""

    pass
