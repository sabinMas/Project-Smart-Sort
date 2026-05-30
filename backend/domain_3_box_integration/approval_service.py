"""Approval and signature orchestration service for Domain 3."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from backend.shared.config import Config
from backend.shared.errors import BoxIntegrationError
from backend.shared.logging import get_logger
from backend.shared.box_utils import BoxFolder, get_folder_id
from backend.shared.docusign_utils import calculate_signature_deadline

logger = get_logger(__name__)


# In-memory store for demo mode
_demo_documents: Dict[str, Dict[str, Any]] = {}
_demo_approvals: Dict[str, List[Dict[str, Any]]] = {}
_demo_signature_states: Dict[str, Dict[str, Any]] = {}


class ApprovalService:
    """Handles document approval workflow."""

    async def review_document(
        self,
        document_id: str,
        action: str,
        final_recipients: List[str],
        reason: Optional[str] = None,
        changes_made: Optional[List[str]] = None,
        approved_by: str = "system@company.com",
    ) -> Dict[str, Any]:
        """Submit a review decision for a document.

        Args:
            document_id: Document ID
            action: approve, reject, flag_for_review, or edit
            final_recipients: Final list of recipient emails
            reason: Decision reason
            changes_made: List of changes made
            approved_by: Email of approver

        Returns:
            Dict with approval_id, status, and next_step
        """
        approval_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # Determine status and next step based on action
        status_map = {
            "approve": ("approved", "ready_to_send_signature_request"),
            "reject": ("rejected", "document_rejected"),
            "flag_for_review": ("flagged", "manual_review_required"),
            "edit": ("approved", "ready_to_send_signature_request"),
        }

        status, next_step = status_map.get(action, ("flagged", "unknown_action"))

        approval_record = {
            "id": approval_id,
            "document_id": document_id,
            "action": action,
            "decision_reason": reason,
            "original_recipients": final_recipients,
            "approved_recipients": final_recipients,
            "changes_made": changes_made or [],
            "approved_by": approved_by,
            "approved_at": now.isoformat(),
        }

        if Config.DEMO_MODE:
            # Store in memory
            if document_id not in _demo_approvals:
                _demo_approvals[document_id] = []
            _demo_approvals[document_id].append(approval_record)

            # Update document status
            if document_id not in _demo_documents:
                _demo_documents[document_id] = {"status": "pending_approval"}
            _demo_documents[document_id]["status"] = status
            _demo_documents[document_id]["approved_by"] = approved_by
            _demo_documents[document_id]["approved_at"] = now.isoformat()

            logger.info(
                f"[DEMO] Document {document_id} {action} by {approved_by}"
            )
        else:
            from backend.shared.database import db

            await db.execute(
                """
                INSERT INTO approvals (id, document_id, action, decision_reason,
                    original_recipients, approved_recipients, changes_made, approved_by)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, $7, $8)
                """,
                uuid.UUID(approval_id),
                uuid.UUID(document_id),
                action,
                reason,
                final_recipients,
                final_recipients,
                changes_made,
                approved_by,
            )

            await db.execute(
                """
                UPDATE documents SET status = $1, approved_by = $2,
                    approved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = $3
                """,
                status,
                approved_by,
                uuid.UUID(document_id),
            )

        return {
            "document_id": document_id,
            "approval_id": approval_id,
            "status": status,
            "next_step": next_step,
        }

    async def get_approval_history(self, document_id: str) -> List[Dict[str, Any]]:
        """Get approval history for a document.

        Args:
            document_id: Document ID

        Returns:
            List of approval records
        """
        if Config.DEMO_MODE:
            return _demo_approvals.get(document_id, [])

        from backend.shared.database import db

        rows = await db.fetch_all(
            """
            SELECT id, action, approved_by, approved_at, decision_reason,
                   original_recipients, approved_recipients, changes_made
            FROM approvals
            WHERE document_id = $1
            ORDER BY approved_at DESC
            """,
            uuid.UUID(document_id),
        )
        return [dict(row) for row in rows]


class SignatureService:
    """Handles DocuSign signature workflow."""

    async def send_for_signature(
        self,
        document_id: str,
        recipients: List[Dict[str, str]],
        expires_days: int = 14,
    ) -> Dict[str, Any]:
        """Send document for signature via DocuSign.

        Args:
            document_id: Document ID
            recipients: List of {email, name, role} dicts
            expires_days: Days until signature expires

        Returns:
            Dict with envelope_id, status, recipients_sent_to, expires_at
        """
        envelope_id = f"envelope_{uuid.uuid4().hex[:12]}"
        expires_at = calculate_signature_deadline()
        now = datetime.now(timezone.utc)

        signature_state = {
            "document_id": document_id,
            "docusign_envelope_id": envelope_id,
            "recipients": [
                {
                    "email": r["email"],
                    "name": r.get("name", ""),
                    "status": "sent",
                    "signed_at": None,
                }
                for r in recipients
            ],
            "signed_count": 0,
            "total_count": len(recipients),
            "expires_at": expires_at.isoformat(),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        if Config.DEMO_MODE:
            _demo_signature_states[document_id] = signature_state

            # Update document status
            if document_id not in _demo_documents:
                _demo_documents[document_id] = {}
            _demo_documents[document_id]["status"] = "sent_for_signature"
            _demo_documents[document_id]["sent_at"] = now.isoformat()
            _demo_documents[document_id]["box_folder_current"] = "needs_signature"

            logger.info(
                f"[DEMO] Sent document {document_id} for signature "
                f"to {len(recipients)} recipients"
            )
        else:
            from backend.shared.database import db

            await db.execute(
                """
                INSERT INTO signature_state
                    (document_id, docusign_envelope_id, recipients,
                     signed_count, total_count, expires_at)
                VALUES ($1, $2, $3::jsonb, $4, $5, $6)
                """,
                uuid.UUID(document_id),
                envelope_id,
                signature_state["recipients"],
                0,
                len(recipients),
                expires_at,
            )

            await db.execute(
                """
                UPDATE documents SET status = 'sent_for_signature',
                    sent_at = CURRENT_TIMESTAMP, expires_at = $1,
                    box_folder_current = 'needs_signature',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
                """,
                expires_at,
                uuid.UUID(document_id),
            )

        return {
            "document_id": document_id,
            "docusign_envelope_id": envelope_id,
            "status": "sent",
            "recipients_sent_to": len(recipients),
            "expires_at": expires_at.isoformat(),
        }

    async def get_signature_status(self, document_id: str) -> Dict[str, Any]:
        """Get current signature status for a document.

        Args:
            document_id: Document ID

        Returns:
            Dict with status, signed_count, total_count, recipients
        """
        if Config.DEMO_MODE:
            state = _demo_signature_states.get(document_id)
            if not state:
                return {
                    "document_id": document_id,
                    "status": "not_found",
                    "signed_count": 0,
                    "total_count": 0,
                    "completion_percentage": 0,
                    "recipients": [],
                }

            total = state["total_count"]
            signed = state["signed_count"]
            pct = int((signed / total * 100)) if total > 0 else 0

            status = "complete" if signed == total else "awaiting_signatures"

            return {
                "document_id": document_id,
                "status": status,
                "signed_count": signed,
                "total_count": total,
                "completion_percentage": pct,
                "recipients": state["recipients"],
            }

        from backend.shared.database import db

        row = await db.fetch_one(
            """
            SELECT document_id, recipients, signed_count, total_count,
                   docusign_envelope_id, expires_at
            FROM signature_state
            WHERE document_id = $1
            """,
            uuid.UUID(document_id),
        )

        if not row:
            return {
                "document_id": document_id,
                "status": "not_found",
                "signed_count": 0,
                "total_count": 0,
                "completion_percentage": 0,
                "recipients": [],
            }

        total = row["total_count"]
        signed = row["signed_count"]
        pct = int((signed / total * 100)) if total > 0 else 0
        status = "complete" if signed == total else "awaiting_signatures"

        return {
            "document_id": str(row["document_id"]),
            "status": status,
            "signed_count": signed,
            "total_count": total,
            "completion_percentage": pct,
            "recipients": row["recipients"],
        }

    async def handle_docusign_webhook(self, event: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DocuSign webhook event.

        Args:
            event: Event type (recipient-completed, envelope-completed, recipient-declined)
            data: Event data with envelopeId, recipientEmail, status, etc.

        Returns:
            Dict with processing status
        """
        envelope_id = data.get("envelopeId", "")
        recipient_email = data.get("recipientEmail", "")
        signed_at = data.get("signedDateTime")

        logger.info(
            f"DocuSign webhook: event={event}, envelope={envelope_id}, "
            f"recipient={recipient_email}"
        )

        if Config.DEMO_MODE:
            # Find the document by envelope_id
            doc_id = None
            for did, state in _demo_signature_states.items():
                if state.get("docusign_envelope_id") == envelope_id:
                    doc_id = did
                    break

            if not doc_id:
                return {"status": "ignored", "reason": "envelope_not_found"}

            state = _demo_signature_states[doc_id]

            if event == "recipient-completed":
                # Update recipient status
                for r in state["recipients"]:
                    if r["email"] == recipient_email:
                        r["status"] = "signed"
                        r["signed_at"] = signed_at or datetime.now(timezone.utc).isoformat()
                        break

                state["signed_count"] = sum(
                    1 for r in state["recipients"] if r["status"] == "signed"
                )
                state["updated_at"] = datetime.now(timezone.utc).isoformat()

                # Check if all signed
                if state["signed_count"] == state["total_count"]:
                    _demo_documents[doc_id]["status"] = "complete"
                    _demo_documents[doc_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                    _demo_documents[doc_id]["box_folder_current"] = "archive"

            elif event == "envelope-completed":
                state["signed_count"] = state["total_count"]
                for r in state["recipients"]:
                    r["status"] = "signed"
                state["updated_at"] = datetime.now(timezone.utc).isoformat()

                _demo_documents[doc_id]["status"] = "complete"
                _demo_documents[doc_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                _demo_documents[doc_id]["box_folder_current"] = "archive"

            elif event == "recipient-declined":
                for r in state["recipients"]:
                    if r["email"] == recipient_email:
                        r["status"] = "declined"
                        break
                state["updated_at"] = datetime.now(timezone.utc).isoformat()

            return {"status": "processed", "event": event, "document_id": doc_id}

        # Live mode
        from backend.shared.database import db

        row = await db.fetch_one(
            "SELECT document_id FROM signature_state WHERE docusign_envelope_id = $1",
            envelope_id,
        )

        if not row:
            return {"status": "ignored", "reason": "envelope_not_found"}

        document_id = row["document_id"]

        if event == "recipient-completed":
            await db.execute(
                """
                UPDATE signature_state
                SET recipients = jsonb_set_element(recipients, recipient, $1),
                    signed_count = signed_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE docusign_envelope_id = $2
                """,
                envelope_id,
            )

        elif event == "envelope-completed":
            await db.execute(
                """
                UPDATE signature_state
                SET signed_count = total_count,
                    all_signed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE docusign_envelope_id = $1
                """,
                envelope_id,
            )
            await db.execute(
                """
                UPDATE documents SET status = 'complete',
                    completed_at = CURRENT_TIMESTAMP,
                    box_folder_current = 'archive',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
                """,
                document_id,
            )

        return {"status": "processed", "event": event, "document_id": str(document_id)}


class DocumentService:
    """Handles document status queries."""

    async def get_document_status(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get complete status of a document.

        Args:
            document_id: Document ID

        Returns:
            Dict with full document state or None if not found
        """
        if Config.DEMO_MODE:
            doc = _demo_documents.get(document_id)
            if not doc:
                # Return a default for any document_id (demo flexibility)
                return {
                    "document_id": document_id,
                    "filename": "unknown.pdf",
                    "status": "classified",
                    "classification": {},
                    "box_folder": "inbox",
                    "signature_status": None,
                    "approvals": _demo_approvals.get(document_id, []),
                }

            sig_state = _demo_signature_states.get(document_id)
            signature_status = None
            if sig_state:
                total = sig_state["total_count"]
                signed = sig_state["signed_count"]
                signature_status = {
                    "signed_count": signed,
                    "total_count": total,
                    "completion_percentage": int((signed / total * 100)) if total > 0 else 0,
                }

            return {
                "document_id": document_id,
                "filename": doc.get("filename", "document.pdf"),
                "status": doc.get("status", "classified"),
                "classification": doc.get("classification", {}),
                "box_folder": doc.get("box_folder_current", "inbox"),
                "signature_status": signature_status,
                "approvals": _demo_approvals.get(document_id, []),
            }

        from backend.shared.database import db

        row = await db.fetch_one(
            """
            SELECT id, file_name, status, classification, box_folder_current,
                   created_at, classified_at, approved_at, sent_at, completed_at
            FROM documents WHERE id = $1
            """,
            uuid.UUID(document_id),
        )

        if not row:
            return None

        return {
            "document_id": str(row["id"]),
            "filename": row["file_name"],
            "status": row["status"],
            "classification": row.get("classification", {}),
            "box_folder": row.get("box_folder_current", ""),
            "signature_status": None,
            "approvals": [],
        }

    async def list_documents(
        self,
        status: Optional[str] = None,
        box_folder: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """List documents with optional filtering.

        Args:
            status: Filter by status
            box_folder: Filter by Box folder
            limit: Max results
            offset: Pagination offset

        Returns:
            Dict with documents list, total count, limit, offset
        """
        if Config.DEMO_MODE:
            docs = []
            for doc_id, doc in _demo_documents.items():
                if status and doc.get("status") != status:
                    continue
                if box_folder and doc.get("box_folder_current") != box_folder:
                    continue
                docs.append({
                    "document_id": doc_id,
                    "filename": doc.get("filename", "document.pdf"),
                    "status": doc.get("status", "classified"),
                    "doc_type": doc.get("doc_type", "other"),
                    "created_at": doc.get("created_at"),
                    "approved_at": doc.get("approved_at"),
                    "sent_at": doc.get("sent_at"),
                })

            total = len(docs)
            docs = docs[offset : offset + limit]

            return {
                "documents": docs,
                "total": total,
                "limit": limit,
                "offset": offset,
            }

        from backend.shared.database import db

        conditions = []
        params = []
        param_idx = 1

        if status:
            conditions.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1

        if box_folder:
            conditions.append(f"box_folder_current = ${param_idx}")
            params.append(box_folder)
            param_idx += 1

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        total = await db.fetch_val(
            f"SELECT COUNT(*) FROM documents {where_clause}", *params
        )

        params.extend([limit, offset])
        rows = await db.fetch_all(
            f"""
            SELECT id, file_name, status, classification_confidence,
                   box_folder_current, created_at, approved_at, sent_at
            FROM documents {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """,
            *params,
        )

        documents = [
            {
                "document_id": str(row["id"]),
                "filename": row["file_name"],
                "status": row["status"],
                "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
                "approved_at": row["approved_at"].isoformat() if row.get("approved_at") else None,
                "sent_at": row["sent_at"].isoformat() if row.get("sent_at") else None,
            }
            for row in rows
        ]

        return {
            "documents": documents,
            "total": total or 0,
            "limit": limit,
            "offset": offset,
        }
