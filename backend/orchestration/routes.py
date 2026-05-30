"""API routes for document orchestration."""

import logging
from fastapi import APIRouter, HTTPException
from .orchestrator import get_orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/orchestrate/{document_id}", tags=["orchestration"])
async def manually_orchestrate(document_id: str) -> dict:
    """
    Manually trigger the orchestration pipeline for a document.

    This endpoint allows re-processing of documents that failed automatically,
    or manually triggering the pipeline for demo/testing purposes.

    Args:
        document_id: UUID of the document to process

    Returns:
        dict with processing results and status
    """
    try:
        logger.info(f"Manual orchestration triggered for document: {document_id}")

        orchestrator = get_orchestrator()

        # Note: In a real implementation, we'd fetch the IngestedDocument from DB
        # For now, this endpoint is a placeholder for the orchestration API
        result = await orchestrator.retry_failed_document(document_id)

        if result is None:
            raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")

        return {
            "status": result.status,
            "document_id": result.document_id,
            "box_file_id": result.box_file_id,
            "destination_folder": result.destination_folder,
            "task_id": result.task_id,
            "assigned_to": result.assigned_to,
            "error_message": result.error_message,
            "completed_at": result.completed_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orchestration error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {e}")
