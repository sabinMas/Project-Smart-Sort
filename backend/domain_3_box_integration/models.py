"""Pydantic models for Domain 3 (Approvals, Signatures & Orchestration)."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class ApprovalRequest(BaseModel):
    """Request to approve a document for signature."""

    document_id: str
    action: str  # "approve", "reject", "flag_for_review", "edit"
    final_recipients: List[EmailStr]
    reason: Optional[str] = None
    changes_made: Optional[List[str]] = None


class ApprovalResponse(BaseModel):
    """Response after approval decision."""

    document_id: str
    approval_id: str
    status: str  # "approved", "rejected", "flagged"
    next_step: str


class SendForSignatureRequest(BaseModel):
    """Request to send document for signature via DocuSign."""

    document_id: str
    recipients: List[dict]  # [{email, name, role}]
    expires_days: int = 14


class SendForSignatureResponse(BaseModel):
    """Response after sending for signature."""

    document_id: str
    docusign_envelope_id: str
    status: str
    recipients_sent_to: int
    expires_at: str  # ISO format datetime string


class SignatureStatusResponse(BaseModel):
    """Current signature status for a document."""

    document_id: str
    status: str
    signed_count: int
    total_count: int
    completion_percentage: int
    recipients: List[dict]


class ApprovalHistoryModel(BaseModel):
    """Single approval record."""

    id: str
    action: str
    approved_by: EmailStr
    approved_at: datetime
    decision_reason: Optional[str] = None


class DocumentStatusResponse(BaseModel):
    """Complete status of a document."""

    document_id: str
    filename: str
    status: str
    classification: dict
    box_folder: str
    signature_status: Optional[SignatureStatusResponse] = None
    approvals: List[ApprovalHistoryModel]
