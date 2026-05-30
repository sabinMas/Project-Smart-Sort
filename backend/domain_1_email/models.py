"""Pydantic models for Domain 1 (Email Ingestion)."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class AttachmentModel(BaseModel):
    """Email attachment model."""

    filename: str
    content_type: str
    content: str  # base64 encoded


class SendGridInboundWebhookModel(BaseModel):
    """SendGrid inbound parse webhook payload."""

    from_: str = Field(alias="from")
    to: str
    subject: str
    text: Optional[str] = None
    html: Optional[str] = None
    attachments: Optional[int] = None
    attachment: Optional[List[AttachmentModel]] = None

    class Config:
        populate_by_name = True


class EmailReturnWebhookModel(BaseModel):
    """Webhook for signed document returns via email."""

    from_: str = Field(alias="from")
    subject: str
    document_id: Optional[str] = None
    attachment_filename: str
    attachment_content: str  # base64 encoded


class DocumentUploadRequest(BaseModel):
    """Request to upload a document (manual upload, not via email)."""

    file_data: str  # base64 encoded
    file_name: str
    source: str = "manual_upload"
    source_email: Optional[EmailStr] = None


class DocumentIngestionResponse(BaseModel):
    """Response after ingesting a document."""

    document_id: str
    filename: str
    status: str
    box_file_id: Optional[str] = None
    classified_at: Optional[datetime] = None
    error: Optional[str] = None
