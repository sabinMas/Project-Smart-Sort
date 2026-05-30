"""
Shared type definitions for Box Smart Inbox.

These types define the contracts between domains and are LOCKED after T+0.
No modifications allowed without consensus from all 3 domain teams.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Literal, Optional
import uuid


@dataclass
class IngestedDocument:
    """
    Output of Domain 1 (Email Ingestion).
    Input to Domain 2 (AI Classification).

    Represents a raw document that has been ingested into the system,
    typically from email or file upload, before classification.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    content: str = ""
    content_type: Literal[
        "text/plain",
        "application/pdf",
        "image/jpeg",
        "image/png",
    ] = "text/plain"
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    source: Literal["email", "box_file_request"] = "email"
    email_from: Optional[str] = None
    file_size_bytes: Optional[int] = None
    raw_file_bytes: Optional[bytes] = None  # Raw file bytes for Box upload

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "filename": self.filename,
            "content": self.content,
            "content_type": self.content_type,
            "uploaded_at": self.uploaded_at.isoformat(),
            "source": self.source,
            "email_from": self.email_from,
            "file_size_bytes": self.file_size_bytes,
        }


@dataclass
class ClassificationResult:
    """
    Output of Domain 2 (AI Classification).
    Input to Domain 3 (Box Integration).

    Represents the result of AI-powered document classification,
    including document type, confidence, and extracted metadata.
    """

    document_id: str
    doc_type: Literal[
        "invoice",
        "contract",
        "resume",
        "receipt",
        "id_document",
        "purchase_order",
        "other",
    ]
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Why the model chose this type
    extracted_fields: dict = field(default_factory=dict)  # e.g., {"vendor": "ACME", "amount": 1500}
    required_reviewer: Optional[str] = None  # "finance", "legal", "hr", "procurement", None
    metadata_tags: list = field(default_factory=list)  # e.g., ["vendor:acme", "q2_2026", "urgent"]
    classified_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate confidence is in range [0.0, 1.0]."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "document_id": self.document_id,
            "doc_type": self.doc_type,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "extracted_fields": self.extracted_fields,
            "required_reviewer": self.required_reviewer,
            "metadata_tags": self.metadata_tags,
            "classified_at": self.classified_at.isoformat(),
        }


@dataclass
class ContactVerification:
    """
    Contact verification result with layered evidence.
    Output of Domain 2 contact resolution layer.
    """

    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    verification_score: int = 0  # 0-100
    verified: bool = False
    source: Literal["email_from", "email_to", "extracted_from_doc", "manual"] = "extracted_from_doc"
    last_contact: Optional[datetime] = None
    evidence: dict = field(default_factory=dict)  # {from_document, from_contact_db, from_email_header}

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "email": self.email,
            "name": self.name,
            "company": self.company,
            "verification_score": self.verification_score,
            "verified": self.verified,
            "source": self.source,
            "last_contact": self.last_contact.isoformat() if self.last_contact else None,
            "evidence": self.evidence,
        }


@dataclass
class SignatureStateRecipient:
    """Single recipient's signature state."""

    email: str
    name: Optional[str] = None
    status: Literal["pending", "sent", "opened", "signed", "declined", "voided"] = "pending"
    signed_at: Optional[datetime] = None
    docusign_id: Optional[str] = None


@dataclass
class SignatureState:
    """
    Signature tracking state for a document.
    Owned by Domain 3, updated by DocuSign webhooks.
    """

    document_id: str
    recipients: list = field(default_factory=list)  # List[SignatureStateRecipient]
    signed_count: int = 0
    total_count: int = 0
    docusign_envelope_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    all_signed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "document_id": self.document_id,
            "recipients": [r.__dict__ if hasattr(r, '__dict__') else r for r in self.recipients],
            "signed_count": self.signed_count,
            "total_count": self.total_count,
            "docusign_envelope_id": self.docusign_envelope_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "all_signed_at": self.all_signed_at.isoformat() if self.all_signed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class ProcessingResult:
    """
    Output of Domain 3 (Box Integration).
    Final result sent to notifications and dashboard.

    Represents the complete outcome of processing a document through
    all three domains: ingestion, classification, and Box integration.
    """

    document_id: str
    box_file_id: str  # ID of file in Box
    destination_folder: str  # e.g., "/Invoices/2026/May/"
    status: Literal["success", "failure", "escalated"]
    task_id: Optional[str] = None  # Box task ID if created
    assigned_to: Optional[str] = None  # Email of assigned reviewer
    metadata_applied: dict = field(default_factory=dict)  # Metadata tags applied to file
    notification_sent_to: list = field(default_factory=list)  # ["slack", "email"]
    error_message: Optional[str] = None
    completed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "document_id": self.document_id,
            "box_file_id": self.box_file_id,
            "destination_folder": self.destination_folder,
            "task_id": self.task_id,
            "assigned_to": self.assigned_to,
            "metadata_applied": self.metadata_applied,
            "notification_sent_to": self.notification_sent_to,
            "status": self.status,
            "error_message": self.error_message,
            "completed_at": self.completed_at.isoformat(),
        }
