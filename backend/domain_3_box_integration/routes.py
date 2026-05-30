"""FastAPI routes for Domain 3 (Approvals, Signatures & Orchestration)."""

import logging
from fastapi import APIRouter, HTTPException, Request
from .models import (
    ApprovalRequest,
    ApprovalResponse,
    SendForSignatureRequest,
    SendForSignatureResponse,
    SignatureStatusResponse,
    DocumentStatusResponse,
)
from .approval_service import ApprovalService, SignatureService, DocumentService

logger = logging.getLogger(__name__)
router = APIRouter()

# Service instances
_approval_service = ApprovalService()
_signature_service = SignatureService()
_document_service = DocumentService()


@router.post("/api/approvals/review", response_model=ApprovalResponse, tags=["approvals"])
async def review_document(request: ApprovalRequest) -> ApprovalResponse:
    """Submit human review decision for a document.

    Actions:
    - approve: Send for signature
    - reject: Move to rejected folder
    - flag_for_review: Mark for manual intervention
    - edit: Modify suggested recipients
    """
    valid_actions = ("approve", "reject", "flag_for_review", "edit")
    if request.action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action '{request.action}'. Must be one of: {valid_actions}",
        )

    try:
        result = await _approval_service.review_document(
            document_id=request.document_id,
            action=request.action,
            final_recipients=[str(e) for e in request.final_recipients],
            reason=request.reason,
            changes_made=request.changes_made,
        )

        return ApprovalResponse(
            document_id=result["document_id"],
            approval_id=result["approval_id"],
            status=result["status"],
            next_step=result["next_step"],
        )
    except Exception as e:
        logger.error(f"Error processing approval for {request.document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/approvals/{document_id}", tags=["approvals"])
async def get_approval_history(document_id: str) -> dict:
    """Get approval history for a document."""
    try:
        approvals = await _approval_service.get_approval_history(document_id)
        return {"approvals": approvals}
    except Exception as e:
        logger.error(f"Error getting approval history for {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/signatures/send", response_model=SendForSignatureResponse, tags=["signatures"])
async def send_for_signature(request: SendForSignatureRequest) -> SendForSignatureResponse:
    """Send document for signature via DocuSign envelope."""
    if not request.recipients:
        raise HTTPException(status_code=400, detail="At least one recipient is required")

    try:
        result = await _signature_service.send_for_signature(
            document_id=request.document_id,
            recipients=request.recipients,
            expires_days=request.expires_days,
        )

        return SendForSignatureResponse(
            document_id=result["document_id"],
            docusign_envelope_id=result["docusign_envelope_id"],
            status=result["status"],
            recipients_sent_to=result["recipients_sent_to"],
            expires_at=result["expires_at"],
        )
    except Exception as e:
        logger.error(f"Error sending {request.document_id} for signature: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/signatures/{document_id}/status", response_model=SignatureStatusResponse, tags=["signatures"])
async def get_signature_status(document_id: str) -> SignatureStatusResponse:
    """Get current signature status for a document."""
    try:
        result = await _signature_service.get_signature_status(document_id)

        if result["status"] == "not_found":
            raise HTTPException(
                status_code=404,
                detail=f"No signature state found for document {document_id}",
            )

        return SignatureStatusResponse(
            document_id=result["document_id"],
            status=result["status"],
            signed_count=result["signed_count"],
            total_count=result["total_count"],
            completion_percentage=result["completion_percentage"],
            recipients=result["recipients"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signature status for {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/docusign", tags=["webhooks"])
async def handle_docusign_webhook(request: Request) -> dict:
    """Handle DocuSign envelope webhook events.

    Events:
    - recipient-completed: One signer finished
    - envelope-completed: All signers finished
    - recipient-declined: Signer declined
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event = body.get("event", "")
    data = body.get("data", {})

    if not event:
        raise HTTPException(status_code=400, detail="Missing 'event' field")

    valid_events = ("recipient-completed", "envelope-completed", "recipient-declined")
    if event not in valid_events:
        logger.warning(f"Unknown DocuSign event: {event}")
        return {"status": "ignored", "reason": f"unknown event: {event}"}

    try:
        result = await _signature_service.handle_docusign_webhook(event, data)
        return result
    except Exception as e:
        logger.error(f"Error handling DocuSign webhook: {e}")
        return {"status": "error", "detail": str(e)}


@router.get("/api/documents/{document_id}", tags=["documents"])
async def get_document_status(document_id: str) -> dict:
    """Get complete status of a document through the pipeline."""
    try:
        result = await _document_service.get_document_status(document_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found",
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document status for {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/documents", tags=["documents"])
async def list_documents(
    status: str = None,
    box_folder: str = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List documents with filtering."""
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 200")
    if offset < 0:
        raise HTTPException(status_code=400, detail="Offset must be non-negative")

    try:
        result = await _document_service.list_documents(
            status=status,
            box_folder=box_folder,
            limit=limit,
            offset=offset,
        )
        return result
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
