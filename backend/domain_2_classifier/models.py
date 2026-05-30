"""Pydantic models for Domain 2 (Classification & Contact Verification)."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ClassifyDocumentRequest(BaseModel):
    """Request to classify a document."""

    document_id: str
    file_content: str  # base64 encoded PDF


class ClassifyDocumentResponse(BaseModel):
    """Response from classification."""

    document_id: str
    doc_type: str
    confidence: float
    suggested_signers: List[str]
    priority: str
    flags: List[str]
    reasoning: str


class ResolveRecipientsRequest(BaseModel):
    """Request to resolve and verify recipient emails."""

    document_id: str
    extracted_emails: List[str]


class VerificationEvidenceModel(BaseModel):
    """Evidence for contact verification."""

    confidence: Optional[float] = None
    location: Optional[str] = None
    verified: Optional[bool] = None
    last_email_date: Optional[datetime] = None


class ResolvedContactModel(BaseModel):
    """A single resolved and verified contact."""

    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    verification_score: int  # 0-100
    verified: bool
    source: str
    last_contact: Optional[datetime] = None
    evidence: dict


class ResolveRecipientsResponse(BaseModel):
    """Response with resolved recipients."""

    resolved_contacts: List[ResolvedContactModel]


class ManualContactVerificationRequest(BaseModel):
    """Manually verify a contact."""

    email: str
    verified: bool
    name: Optional[str] = None
    company: Optional[str] = None
    tags: Optional[List[str]] = None
