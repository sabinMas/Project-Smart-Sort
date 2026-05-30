# 3-Domain Architecture for Document Orchestration

## Overview

The project is divided into 3 independent domains that communicate via type contracts and REST APIs. Each domain can be developed, tested, and deployed independently.

```
┌─────────────────────────┐
│   Domain 1: Email       │
│   Ingest & Returns      │
├─────────────────────────┤
│ SendGrid webhook        │
│ PDF extraction          │
│ File deduplication      │
│ Box upload (inbox)      │
│ Email return handling   │
│ Signature extraction    │
└──────────┬──────────────┘
           │ IngestedDocument
           ▼
┌─────────────────────────┐
│   Domain 2:             │
│   Classification &      │
│   Contact Verification  │
├─────────────────────────┤
│ Claude classification   │
│ Email extraction (OCR)  │
│ 3-layer verification    │
│ Contact database        │
└──────────┬──────────────┘
           │ ClassificationResult
           │ + ContactVerification[]
           ▼
┌─────────────────────────┐
│   Domain 3:             │
│   Approvals, Signatures │
│   & Orchestration       │
├─────────────────────────┤
│ Human approval workflow │
│ Box folder management   │
│ DocuSign envelope       │
│ Signature tracking      │
│ Reminders & expiry      │
│ Archive workflow        │
└─────────────────────────┘
```

## Domain 1: Email Ingestion & Return Handling

**Ownership:** Incoming email processing and signed document returns

**Responsibilities:**
- Receive emails via SendGrid webhook
- Extract PDF/document attachments
- Compute SHA-256 file hash for deduplication
- Upload to Box inbox folder
- Track sender email in contact_emails table
- Log all inbound email activity
- Handle email returns with signed PDFs
- Extract signatures via OCR
- Match returned documents to originals

**Type Contract:**
- **Input:** Raw email from SendGrid webhook
- **Output:** `IngestedDocument` (locked in types.py)

**Database Tables:**
- Reads: none
- Writes: documents.file_hash, contact_emails (email_from), email_audit_log

**API Endpoints:**
- `POST /webhooks/sendgrid` - Inbound email handler
- `POST /webhooks/email-return` - Signed PDF returns
- `POST /api/documents/upload` - Manual upload (testing)
- `GET /api/documents/pending-return` - List awaiting returns

**Key Files:**
- `backend/domain_1_email/service.py` - EmailIngestionService
- `backend/domain_1_email/email_return_handler.py` - SignedDocumentHandler
- `backend/domain_1_email/signature_extractor.py` - OCR for signatures
- `backend/domain_1_email/routes.py` - FastAPI endpoints
- `backend/domain_1_email/models.py` - Pydantic models

**Dependencies:**
- SendGrid SDK
- PyPDF2 or pdfplumber (PDF parsing)
- pytesseract (OCR for signatures)
- Box SDK

## Domain 2: Classification & Contact Verification

**Ownership:** Document classification and contact verification

**Responsibilities:**
- Classify documents using Claude API
- Fallback chain: Claude Sonnet → Claude Haiku → Box AI
- Extract email addresses from PDF content
- Verify contacts with 3-layer evidence
- Manage contact database (upsert, dedup, verify)
- Calculate verification scores (0-100)
- Provide recipient verification to Domain 3

**Type Contract:**
- **Input:** `IngestedDocument` (from Domain 1)
- **Output:** `ClassificationResult` + `ContactVerification[]` (locked in types.py)

**Database Tables:**
- Reads: contact_emails (for verification)
- Writes: documents.classification, contact_emails (verified contacts)

**API Endpoints:**
- `POST /api/classify` - Classify document
- `POST /api/contacts/resolve` - Resolve & verify recipients
- `POST /api/contacts/verify` - Manual verification
- `GET /api/contacts` - Query contact database

**3-Layer Contact Verification:**
1. **From Document** (OCR confidence: 0.0-1.0)
   - Extract emails from PDF content
   - Confidence based on OCR quality
   
2. **From Contact DB** (historical data)
   - Lookup in contact_emails table
   - Higher score if previously verified
   
3. **From Email Header** (source email)
   - Extract from original SendGrid email
   - Highest confidence if sender

**Key Files:**
- `backend/domain_2_classifier/service.py` - ClassificationService
- `backend/domain_2_classifier/contact_resolver.py` - ContactResolutionService
- `backend/domain_2_classifier/verification_engine.py` - 3-layer verification
- `backend/domain_2_classifier/email_extractor.py` - PDF email extraction
- `backend/domain_2_classifier/llm_router.py` - LLM provider fallback
- `backend/domain_2_classifier/prompts.py` - Claude prompts
- `backend/domain_2_classifier/routes.py` - FastAPI endpoints
- `backend/domain_2_classifier/models.py` - Pydantic models

**Dependencies:**
- Anthropic SDK (Claude API)
- pdfplumber or pytesseract (PDF extraction)
- asyncpg (database)

## Domain 3: Approvals, Signatures & Orchestration

**Ownership:** Approval workflow, DocuSign integration, signature tracking

**Responsibilities:**
- Host approval workflow UI
- Receive human approval decisions
- Move files in Box between folders (inbox → needs_review → needs_signature → archive)
- Create metadata files in Box (*.metadata.json, *.recipients.json, *.state.json)
- Create and send DocuSign envelopes
- Track signature state (recipients, signed_count, expiry)
- Handle DocuSign webhook events (recipient-completed, envelope-completed)
- Send reminder emails at 7-day intervals
- Detect expiry at 14-day mark
- Archive completed documents
- Orchestrate Strand Agents for long-running tasks

**Type Contract:**
- **Input:** `ClassificationResult` + `ContactVerification[]` (from Domain 2)
- **Output:** `ProcessingResult` (for audit and notifications)

**Database Tables:**
- Reads: documents, contact_emails
- Writes: documents (status, approved_by), signature_state, approvals, email_audit_log

**API Endpoints:**
- `POST /api/approvals/review` - Submit approval decision
- `GET /api/approvals/{document_id}` - Get approval history
- `POST /api/signatures/send` - Send for signature
- `GET /api/signatures/{document_id}/status` - Check signature status
- `POST /webhooks/docusign` - DocuSign webhook handler
- `GET /api/documents/{document_id}` - Get document status
- `GET /api/documents` - List documents with filters

**Document State Machine:**
```
ingest → classified → pending_approval → approved
                                ↓
                          sent_for_signature
                                ↓
                         awaiting_return
                                ↓
                            complete → archive
                         
Alternative paths:
pending_approval → rejected → archive
pending_approval → flagged_for_review
```

**Signature State Machine:**
```
pending → sent → in_progress → completed
              ↓
          declined
              ↓
              voided
```

**Key Files:**
- `backend/domain_3_box_integration/service.py` - Main orchestrator
- `backend/domain_3_box_integration/approval_handler.py` - ApprovalService
- `backend/domain_3_box_integration/box_manager.py` - Box operations
- `backend/domain_3_box_integration/docusign_manager.py` - DocuSign envelope
- `backend/domain_3_box_integration/signature_tracker.py` - State tracking
- `backend/domain_3_box_integration/email_manager.py` - Reminders
- `backend/domain_3_box_integration/strand_agents.py` - Orchestration
- `backend/domain_3_box_integration/routes.py` - FastAPI endpoints
- `backend/domain_3_box_integration/models.py` - Pydantic models

**Dependencies:**
- DocuSign SDK
- Box SDK
- SendGrid SDK (for reminders)
- Strand API (for agent orchestration)
- asyncpg (database)

## Type Contracts (Locked)

All inter-domain communication happens via locked types in `backend/shared/types.py`:

### IngestedDocument
Output of Domain 1, input to Domain 2
```python
IngestedDocument(
    id: str,
    filename: str,
    content: str,
    content_type: Literal["text/plain", "application/pdf", ...],
    source: Literal["email", "box_file_request"],
    email_from: Optional[str],
    uploaded_at: datetime
)
```

### ClassificationResult
Output of Domain 2, input to Domain 3
```python
ClassificationResult(
    document_id: str,
    doc_type: Literal["invoice", "contract", ...],
    confidence: float,  # 0.0-1.0
    reasoning: str,
    extracted_fields: dict,
    required_reviewer: Optional[str],
    metadata_tags: list,
    classified_at: datetime
)
```

### ContactVerification
Output of Domain 2 contact resolution
```python
ContactVerification(
    email: str,
    name: Optional[str],
    company: Optional[str],
    verification_score: int,  # 0-100
    verified: bool,
    source: Literal["email_from", "email_to", "extracted_from_doc", "manual"],
    evidence: dict  # {from_document, from_contact_db, from_email_header}
)
```

### ProcessingResult
Output of Domain 3, final result
```python
ProcessingResult(
    document_id: str,
    box_file_id: str,
    destination_folder: str,
    status: Literal["success", "failure", "escalated"],
    task_id: Optional[str],
    assigned_to: Optional[str],
    metadata_applied: dict,
    notification_sent_to: list,
    completed_at: datetime
)
```

## Database Tables

### documents (owned by Domain 3)
- Core document state and lifecycle
- Tracks through all 4 tiers of processing
- Holds classification results as JSONB

### contact_emails (owned by Domain 2)
- Verified contacts built from email traffic
- Verification score and history
- Tags and metadata

### signature_state (owned by Domain 3)
- Tracks signing progress per document
- Recipients and their signing status
- DocuSign envelope ID and expiry

### approvals (owned by Domain 3)
- Audit trail of human decisions
- Records what changed vs. suggested

### email_audit_log (owned by Domains 1 & 3)
- Complete audit of email traffic
- Inbound (Domain 1) and outbound (Domain 3)
- Tracks attachments and status

## Development Workflow

### Phase 1: Foundation (Complete)
- Database schema and migrations
- Shared utilities and type contracts
- Directory structure
- Configuration system

### Phase 2: Domain 1 Implementation
- SendGrid webhook handler
- PDF extraction
- Box upload
- Email logging

### Phase 3: Domain 2 Implementation
- Claude classification
- Email extraction from PDF
- 3-layer contact verification
- Contact database queries

### Phase 4: Domain 3 Implementation
- Approval workflow
- Box folder management
- DocuSign integration
- Signature state tracking

### Phase 5: Automation & Polish
- Reminder scheduler
- Expiry detection
- Email returns handling
- Archive automation
- Strand Agent orchestration

## Testing Strategy

### Unit Tests
Each domain has unit tests in its `tests/` directory:
- `backend/domain_1_email/tests/test_service.py`
- `backend/domain_2_classifier/tests/test_service.py`
- `backend/domain_3_box_integration/tests/test_service.py`

### Integration Tests
Full workflow tests in `backend/tests/`:
- `test_integration_e2e.py` - End-to-end flow from email to archive

### Test Fixtures
- `backend/shared/fixtures.py` - Pytest fixtures
- `backend/shared/test_documents.py` - Sample PDFs

## Key Design Principles

1. **Domain Isolation:** No cross-domain imports except via type contracts
2. **Type Safety:** Pydantic models enforce contracts
3. **State Persistence:** Database as single source of truth
4. **Error Handling:** Fallback chains for LLM and external services
5. **Audit Trail:** Complete logging of all operations
6. **Async/Await:** All services are async-ready
7. **Configuration:** Environment-based config, no hardcoding
