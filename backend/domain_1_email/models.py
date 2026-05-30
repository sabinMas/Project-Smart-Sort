"""Pydantic models for Domain 1: Email Ingestion."""

from typing import Optional, List
from pydantic import BaseModel, Field


class EmailAttachment(BaseModel):
    """Represents an attachment in an email."""

    filename: str = Field(..., description="Name of the attachment file")
    content_type: str = Field(..., description="MIME type (e.g., application/pdf)")
    size_bytes: int = Field(..., description="File size in bytes")
    content: Optional[bytes] = Field(None, description="File content (base64 encoded)")


class EmailPayload(BaseModel):
    """Represents the raw email payload from SendGrid webhook."""

    headers: dict = Field(default_factory=dict, description="Email headers")
    from_email: str = Field(..., description="Sender email address", alias="from")
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    text: Optional[str] = Field(None, description="Plain text body")
    html: Optional[str] = Field(None, description="HTML body")
    attachments: List[EmailAttachment] = Field(default_factory=list, description="Email attachments")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WebhookResponse(BaseModel):
    """Response from webhook endpoint."""

    status: str = Field(..., description="Status: success or error")
    document_id: Optional[str] = Field(None, description="ID of ingested document")
    message: str = Field(..., description="Response message")
