"""Pydantic schemas for Domain 2: AI Classification."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ClassificationRequest(BaseModel):
    """Request to classify a document."""

    document_id: str = Field(..., description="Unique document ID")
    document_text: str = Field(..., description="Full text content of the document")
    document_type_hint: Optional[str] = Field(None, description="Optional hint about document type")


class ExtractedField(BaseModel):
    """A field extracted from the document."""

    key: str = Field(..., description="Field key (e.g., 'vendor', 'amount')")
    value: Any = Field(..., description="Extracted value")
    confidence: float = Field(..., description="Confidence score for this extraction")


class ClassificationResponse(BaseModel):
    """Response from document classification."""

    document_id: str = Field(..., description="Document ID being classified")
    doc_type: str = Field(..., description="Classified document type")
    confidence: float = Field(..., description="Classification confidence (0.0-1.0)")
    reasoning: str = Field(..., description="Explanation of classification decision")
    extracted_fields: Dict[str, Any] = Field(default_factory=dict, description="Extracted key-value pairs")
    required_reviewer: Optional[str] = Field(None, description="Suggested reviewer role")
    metadata_tags: List[str] = Field(default_factory=list, description="Suggested metadata tags")
