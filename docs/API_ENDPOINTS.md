# API Endpoints Reference

## Base URL
```
http://localhost:8000
```

## Health & Status

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "box-smart-inbox",
  "environment": "development"
}
```

### GET /status
System status and statistics.

**Response:**
```json
{
  "status": "operational",
  "documents_total": 42,
  "documents_completed": 15,
  "success_rate": "35.7%"
}
```

---

## Domain 1: Email Ingestion & Returns

### POST /webhooks/sendgrid
Handle inbound emails from SendGrid.

**Headers:**
- `X-Twilio-Email-Event-Webhook-Signature`: Webhook signature for verification

**Request Body:**
```json
{
  "from": "alice@acmecorp.com",
  "to": "documents@company.com",
  "subject": "Contract for signature",
  "text": "Please sign attached contract",
  "attachments": [
    {
      "filename": "contract.pdf",
      "content_type": "application/pdf",
      "content": "base64_encoded_content"
    }
  ]
}
```

**Response:** 200 OK
```json
{
  "status": "received",
  "document_id": "uuid",
  "filename": "contract.pdf"
}
```

### POST /webhooks/email-return
Handle signed documents returning via email.

**Request Body:**
```json
{
  "from": "alice@acmecorp.com",
  "subject": "RE: Contract for signature - SIGNED",
  "document_id": "uuid",
  "attachment_filename": "contract-signed.pdf",
  "attachment_content": "base64_encoded_content"
}
```

**Response:** 200 OK
```json
{
  "status": "processed",
  "document_id": "uuid",
  "signatures_detected": 2
}
```

### POST /api/documents/upload
Manually upload a document (for testing).

**Request Body:**
```json
{
  "file_data": "base64_encoded_pdf",
  "file_name": "contract.pdf",
  "source": "manual_upload",
  "source_email": "alice@acmecorp.com"
}
```

**Response:** 200 OK
```json
{
  "document_id": "uuid",
  "filename": "contract.pdf",
  "status": "ingested",
  "box_file_id": "123456",
  "error": null
}
```

### GET /api/documents/pending-return
List documents awaiting signed returns.

**Query Parameters:**
- `limit` (optional, default=50): Maximum results
- `offset` (optional, default=0): Pagination offset

**Response:** 200 OK
```json
{
  "documents": [
    {
      "document_id": "uuid",
      "filename": "contract.pdf",
      "sent_at": "2026-05-29T20:30:00Z",
      "expires_at": "2026-06-12T20:30:00Z",
      "pending_signers": ["bob@acmecorp.com"]
    }
  ],
  "total": 5,
  "limit": 50,
  "offset": 0
}
```

---

## Domain 2: Classification & Contact Verification

### POST /api/classify
Classify a document using Claude AI.

**Request Body:**
```json
{
  "document_id": "uuid",
  "file_content": "base64_encoded_pdf"
}
```

**Response:** 200 OK
```json
{
  "document_id": "uuid",
  "doc_type": "service_agreement",
  "confidence": 0.94,
  "suggested_signers": [
    "alice@acmecorp.com",
    "bob@acmecorp.com"
  ],
  "priority": "high",
  "flags": [],
  "reasoning": "Multi-party agreement with service terms and liability clauses"
}
```

### POST /api/contacts/resolve
Resolve and verify recipient emails.

**Request Body:**
```json
{
  "document_id": "uuid",
  "extracted_emails": [
    "alice@acmecorp.com",
    "bob@acmecorp.com"
  ]
}
```

**Response:** 200 OK
```json
{
  "resolved_contacts": [
    {
      "email": "alice@acmecorp.com",
      "name": "Alice Smith",
      "company": "Acme Corp",
      "verification_score": 95,
      "verified": true,
      "source": "email_from",
      "last_contact": "2026-05-15T10:30:00Z",
      "evidence": {
        "from_document": {
          "confidence": 0.94,
          "location": "signature_block"
        },
        "from_contact_db": {
          "verified": true,
          "last_email_date": "2026-05-15"
        },
        "from_email_header": null
      }
    },
    {
      "email": "bob@acmecorp.com",
      "name": null,
      "company": "Acme Corp",
      "verification_score": 72,
      "verified": false,
      "source": "extracted_from_doc",
      "last_contact": null,
      "evidence": {
        "from_document": {
          "confidence": 0.87,
          "location": "body_text"
        },
        "from_contact_db": null,
        "from_email_header": null
      }
    }
  ]
}
```

### POST /api/contacts/verify
Manually verify a contact.

**Request Body:**
```json
{
  "email": "alice@acmecorp.com",
  "verified": true,
  "name": "Alice Smith",
  "company": "Acme Corp",
  "tags": ["signer", "primary_contact"]
}
```

**Response:** 200 OK
```json
{
  "email": "alice@acmecorp.com",
  "verified": true,
  "verification_score": 95,
  "tags": ["signer", "primary_contact"]
}
```

### GET /api/contacts
Query contacts in the database.

**Query Parameters:**
- `verified` (optional): true/false to filter
- `limit` (optional, default=100): Maximum results
- `offset` (optional, default=0): Pagination

**Response:** 200 OK
```json
{
  "contacts": [
    {
      "email": "alice@acmecorp.com",
      "name": "Alice Smith",
      "company": "Acme Corp",
      "verified": true,
      "verification_score": 95,
      "email_count": 5,
      "signature_count": 2,
      "last_contact": "2026-05-15T10:30:00Z"
    }
  ],
  "total": 42,
  "limit": 100,
  "offset": 0
}
```

---

## Domain 3: Approvals, Signatures & Orchestration

### POST /api/approvals/review
Submit human approval decision.

**Request Body:**
```json
{
  "document_id": "uuid",
  "action": "approve",
  "final_recipients": [
    "alice@acmecorp.com",
    "bob@acmecorp.com"
  ],
  "reason": "Verified with internal records",
  "changes_made": ["Removed charlie@, added manager@"]
}
```

**Response:** 200 OK
```json
{
  "document_id": "uuid",
  "approval_id": "uuid",
  "status": "approved",
  "next_step": "ready_to_send_signature_request"
}
```

**Actions:**
- `approve`: Send for signature
- `reject`: Move to rejected folder
- `flag_for_review`: Mark for manual intervention
- `edit`: Modify suggested recipients

### GET /api/approvals/{document_id}
Get approval history for a document.

**Response:** 200 OK
```json
{
  "approvals": [
    {
      "id": "uuid",
      "action": "approve",
      "approved_by": "alice@acmecorp.com",
      "approved_at": "2026-05-29T20:00:00Z",
      "decision_reason": "Verified with internal records",
      "original_recipients": ["alice@", "bob@"],
      "approved_recipients": ["alice@", "bob@"]
    }
  ]
}
```

### POST /api/signatures/send
Send document for signature via DocuSign.

**Request Body:**
```json
{
  "document_id": "uuid",
  "recipients": [
    {
      "email": "alice@acmecorp.com",
      "name": "Alice Smith",
      "role": "signer"
    },
    {
      "email": "bob@acmecorp.com",
      "name": "Bob Jones",
      "role": "signer"
    }
  ],
  "expires_days": 14
}
```

**Response:** 200 OK
```json
{
  "document_id": "uuid",
  "docusign_envelope_id": "envelope_id",
  "status": "sent",
  "recipients_sent_to": 2,
  "expires_at": "2026-06-12T20:00:00Z"
}
```

### GET /api/signatures/{document_id}/status
Get current signature status.

**Response:** 200 OK
```json
{
  "document_id": "uuid",
  "status": "awaiting_signatures",
  "signed_count": 1,
  "total_count": 2,
  "completion_percentage": 50,
  "recipients": [
    {
      "email": "alice@acmecorp.com",
      "status": "signed",
      "signed_at": "2026-05-30T10:15:00Z"
    },
    {
      "email": "bob@acmecorp.com",
      "status": "sent",
      "sent_at": "2026-05-29T20:30:00Z"
    }
  ]
}
```

**Recipient Statuses:**
- `pending`: Not yet sent
- `sent`: Email delivered
- `opened`: Recipient opened email
- `signed`: Signature received
- `declined`: Recipient declined
- `voided`: Signature invalidated

### POST /webhooks/docusign
Handle DocuSign webhook events.

**Headers:**
- `X-DocuSign-Signature-1`: Webhook signature

**Request Body:**
```json
{
  "event": "recipient-completed",
  "data": {
    "envelopeId": "envelope_id",
    "recipientEmail": "alice@acmecorp.com",
    "status": "completed",
    "signedDateTime": "2026-05-30T10:15:00Z"
  }
}
```

**Response:** 200 OK
```json
{
  "status": "received"
}
```

**Events:**
- `recipient-completed`: One signer finished
- `envelope-completed`: All signers finished
- `recipient-declined`: Signer declined

### GET /api/documents/{document_id}
Get complete status of a document.

**Response:** 200 OK
```json
{
  "document_id": "uuid",
  "filename": "contract.pdf",
  "status": "sent_for_signature",
  "classification": {
    "doc_type": "service_agreement",
    "confidence": 0.94,
    "suggested_signers": ["alice@", "bob@"],
    "priority": "high"
  },
  "box_folder": "needs_signature",
  "signature_status": {
    "signed_count": 1,
    "total_count": 2,
    "completion_percentage": 50
  },
  "approvals": [
    {
      "id": "uuid",
      "action": "approve",
      "approved_by": "alice@acmecorp.com",
      "approved_at": "2026-05-29T20:00:00Z"
    }
  ]
}
```

### GET /api/documents
List documents with filtering.

**Query Parameters:**
- `status` (optional): Filter by status
- `box_folder` (optional): Filter by Box folder
- `limit` (optional, default=50): Maximum results
- `offset` (optional, default=0): Pagination

**Statuses:**
- `classified`: Just classified, needs review
- `pending_approval`: Waiting for human approval
- `approved`: Approved by human
- `sent_for_signature`: Sent to DocuSign
- `awaiting_return`: Waiting for signed copy
- `complete`: All signatures received
- `rejected`: Rejected by human
- `expired`: Signature deadline passed

**Response:** 200 OK
```json
{
  "documents": [
    {
      "document_id": "uuid",
      "filename": "contract.pdf",
      "status": "sent_for_signature",
      "doc_type": "service_agreement",
      "created_at": "2026-05-29T20:00:00Z",
      "approved_at": "2026-05-29T20:15:00Z",
      "sent_at": "2026-05-29T20:30:00Z"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

---

## Error Responses

All endpoints return standard error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request body"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid webhook signature"
}
```

### 404 Not Found
```json
{
  "detail": "Document uuid not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error": "error details"
}
```
