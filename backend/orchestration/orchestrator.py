"""Document orchestration service - chains Domain 2 and Domain 3 automatically."""

import logging
from datetime import datetime
from typing import Optional

from backend.shared.types import IngestedDocument, ClassificationResult, ProcessingResult
from backend.shared.database import db
from backend.shared.config import Config
from backend.domain_2_classifier.service import ClassificationService
from backend.domain_3_box_integration.service import BoxIntegrationService

logger = logging.getLogger(__name__)

# Confidence threshold - documents below this are marked for manual review
CONFIDENCE_THRESHOLD = 0.80


class DocumentOrchestrator:
    """
    Orchestrates the automatic pipeline:
    Domain 1 (Ingest) → Domain 2 (Classify) → Domain 3 (Route to Box)

    Responsible for:
    1. Taking an ingested document from Domain 1
    2. Automatically classifying it with Domain 2
    3. Automatically routing to Box with Domain 3
    4. Tracking state in database through the pipeline
    5. Handling errors gracefully
    """

    def __init__(self):
        """Initialize orchestrator with service instances."""
        self.classifier = ClassificationService()
        self.box_integration = BoxIntegrationService()

    async def process_ingested_document(
        self, document: IngestedDocument
    ) -> Optional[ProcessingResult]:
        """
        Process a single ingested document through the entire pipeline.

        Args:
            document: IngestedDocument from Domain 1 (email ingestion)

        Returns:
            ProcessingResult with Box routing details, or None if failed

        Flow:
            1. Classify document with Domain 2
            2. Store classification in database
            3. Check confidence threshold
            4. Route to Box with Domain 3 (if confidence >= threshold)
            5. Store routing result in database
            6. Return full result
        """
        logger.info(f"Starting orchestration for document: {document.id}")

        try:
            # Step 1: CLASSIFY (Domain 2)
            logger.info(f"Step 1/3: Classifying document {document.id}...")
            classification = await self.classifier.classify(document)
            logger.info(
                f"  ✓ Classification result: {classification.doc_type} "
                f"({classification.confidence:.0%} confidence)"
            )

            # Step 2: STORE CLASSIFICATION IN DATABASE
            logger.info(f"Step 2/3: Storing classification in database...")
            if not Config.DEMO_MODE:
                try:
                    await db.execute(
                        """
                        UPDATE documents
                        SET classification = %s,
                            status = 'classified',
                            classification_confidence = %s,
                            classified_at = %s,
                            needs_manual_review = %s
                        WHERE id = %s
                        """,
                        (
                            classification.dict(),
                            classification.confidence,
                            datetime.utcnow(),
                            classification.confidence < CONFIDENCE_THRESHOLD,
                            document.id,
                        ),
                    )
                    logger.info(f"  ✓ Classification stored in database")
                except Exception as e:
                    logger.warning(f"Could not store in database (DEMO_MODE): {e}")
            else:
                logger.info(f"  ℹ️ DEMO_MODE: Skipping database update")

            # Step 3: CHECK CONFIDENCE & ROUTE TO BOX (Domain 3)
            if classification.confidence >= CONFIDENCE_THRESHOLD:
                logger.info(f"Step 3/3: Routing to Box (confidence >= {CONFIDENCE_THRESHOLD:.0%})...")

                # Call Domain 3 to route to Box, passing raw bytes for actual upload
                processing_result = await self.box_integration.process(
                    classification,
                    raw_file_bytes=document.raw_file_bytes,
                    filename=document.filename,
                )
                logger.info(
                    f"  ✓ Routed to Box: {processing_result.destination_folder} "
                    f"(File ID: {processing_result.box_file_id})"
                )

                # Step 4: STORE ROUTING RESULT IN DATABASE
                if not Config.DEMO_MODE:
                    try:
                        await db.execute(
                            """
                            UPDATE documents
                            SET status = 'routed_to_box',
                                box_file_id = %s,
                                box_folder_current = %s,
                                routed_at = %s
                            WHERE id = %s
                            """,
                            (
                                processing_result.box_file_id,
                                processing_result.destination_folder,
                                datetime.utcnow(),
                                document.id,
                            ),
                        )
                        logger.info(f"  ✓ Routing result stored in database")
                    except Exception as e:
                        logger.warning(f"Could not store routing in database: {e}")

                logger.info(
                    f"✅ Orchestration complete: {document.filename} "
                    f"→ {classification.doc_type} → {processing_result.destination_folder}"
                )
                return processing_result

            else:
                # Low confidence - mark for manual review
                logger.warning(
                    f"Confidence below threshold ({classification.confidence:.0%} < {CONFIDENCE_THRESHOLD:.0%}). "
                    f"Marking for manual review."
                )

                if not Config.DEMO_MODE:
                    try:
                        await db.execute(
                            """
                            UPDATE documents
                            SET status = 'pending_manual_review',
                                needs_manual_review = TRUE,
                                reviewed_at = %s
                            WHERE id = %s
                            """,
                            (datetime.utcnow(), document.id),
                        )
                    except Exception as e:
                        logger.warning(f"Could not update manual review flag: {e}")

                # Return a partial result indicating manual review needed
                return ProcessingResult(
                    document_id=document.id,
                    box_file_id=None,
                    destination_folder="pending_manual_review",
                    status="pending_manual_review",
                    task_id=None,
                    assigned_to=None,
                    metadata_applied={},
                    notification_sent_to=[],
                    error_message=f"Confidence ({classification.confidence:.0%}) below threshold ({CONFIDENCE_THRESHOLD:.0%})",
                    completed_at=datetime.utcnow(),
                )

        except Exception as e:
            logger.error(f"Orchestration failed for {document.id}: {e}", exc_info=True)

            # Mark document as failed
            if not Config.DEMO_MODE:
                try:
                    await db.execute(
                        """
                        UPDATE documents
                        SET status = 'failed_orchestration',
                            needs_manual_review = TRUE,
                            error_message = %s
                        WHERE id = %s
                        """,
                        (str(e), document.id),
                    )
                except Exception as db_error:
                    logger.error(f"Could not update failure status: {db_error}")

            # Return failure result
            return ProcessingResult(
                document_id=document.id,
                box_file_id=None,
                destination_folder=None,
                status="failed",
                task_id=None,
                assigned_to=None,
                metadata_applied={},
                notification_sent_to=[],
                error_message=str(e),
                completed_at=datetime.utcnow(),
            )

    async def retry_failed_document(self, document_id: str) -> Optional[ProcessingResult]:
        """
        Retry processing a document that failed previously.

        Args:
            document_id: ID of the document to retry

        Returns:
            ProcessingResult from retry attempt
        """
        logger.info(f"Retrying failed document: {document_id}")

        try:
            # Fetch the document from database
            if not Config.DEMO_MODE:
                document_data = await db.fetch_one(
                    "SELECT * FROM documents WHERE id = %s",
                    (document_id,),
                )
                if not document_data:
                    logger.error(f"Document not found: {document_id}")
                    return None

                # Reconstruct IngestedDocument from stored data
                document = IngestedDocument(
                    id=document_data["id"],
                    filename=document_data["file_name"],
                    content=document_data.get("content", ""),
                    content_type=document_data.get("mime_type", "application/octet-stream"),
                    source="retry",
                    email_from=document_data.get("created_by"),
                    file_size_bytes=document_data.get("file_size"),
                )
            else:
                # Demo mode: create a minimal document
                logger.info("DEMO_MODE: Using mock document for retry")
                document = IngestedDocument(
                    id=document_id,
                    filename=f"document_{document_id}",
                    content="Sample content for retry",
                    content_type="text/plain",
                    source="retry",
                )

            # Retry the full orchestration
            return await self.process_ingested_document(document)

        except Exception as e:
            logger.error(f"Retry failed for document {document_id}: {e}")
            return None


# Singleton instance
_orchestrator: Optional[DocumentOrchestrator] = None


def get_orchestrator() -> DocumentOrchestrator:
    """Get or create orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = DocumentOrchestrator()
    return _orchestrator
