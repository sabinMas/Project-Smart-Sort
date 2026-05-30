# Box Smart Inbox - System Flow & Architecture

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│                       COMPANY'S BOX ACCOUNT                       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  User: "Here's an invoice from Acme Corp"               │   │
│  │  Action: Forwards email to system                        │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  SendGrid ◄───┼─── Email webhook
                    │ (Email Parser)│
                    └───────┬───────┘
                            │
                            ▼
        ╔═════════════════════════════════════════════════╗
        ║   BACKEND DOMAIN 1: EMAIL INGESTION            ║
        ║   ─────────────────────────────────            ║
        ║   • Receive SendGrid webhook                   ║
        ║   • Extract email content                      ║
        ║   • Parse attachments (PDF/images)            ║
        ║   • OCR text extraction                        ║
        ║   → Output: IngestedDocument                   ║
        ╚═════════════════════════════════════════════════╝
                            │
                  ┌─────────┴──────────┐
                  │ IngestedDocument   │
                  │ ─────────────────  │
                  │ id: uuid           │
                  │ filename: invoice  │
                  │ content: "Invoice  │
                  │   from Acme..."    │
                  │ content_type: pdf  │
                  │ source: email      │
                  │ email_from: bob@..│
                  └─────────┬──────────┘
                            │
                            ▼
        ╔═════════════════════════════════════════════════╗
        ║   BACKEND DOMAIN 2: AI CLASSIFICATION          ║
        ║   ──────────────────────────────────           ║
        ║   • Call LLM (Cerebras/Groq/Gemini)           ║
        ║   • Llama 3.1 8B classification               ║
        ║   • Extract fields (vendor, amount, date)     ║
        ║   • Assign reviewer (finance/legal/hr)        ║
        ║   → Output: ClassificationResult              ║
        ╚═════════════════════════════════════════════════╝
                            │
                  ┌─────────┴──────────────┐
                  │ ClassificationResult   │
                  │ ──────────────────────│
                  │ document_id: uuid      │
                  │ doc_type: "invoice"    │
                  │ confidence: 0.95       │
                  │ extracted_fields: {    │
                  │   vendor: "Acme",     │
                  │   amount: 5000,        │
                  │   date: "2024-05-29"  │
                  │ }                      │
                  │ required_reviewer:     │
                  │   "finance"            │
                  │ metadata_tags: [       │
                  │   "vendor:acme",       │
                  │   "q2_2026",           │
                  │   "urgent"             │
                  │ ]                      │
                  └─────────┬──────────────┘
                            │
                            ▼
        ╔═════════════════════════════════════════════════╗
        ║   BACKEND DOMAIN 3: BOX INTEGRATION            ║
        ║   ────────────────────────────────             ║
        ║   • Route file to correct folder               ║
        ║     /Invoices/2026/May/                        ║
        ║   • Upload file to Box                         ║
        ║   • Apply metadata tags                        ║
        ║   • Create review task                         ║
        ║   • Assign to finance team member              ║
        ║   • Send notifications                         ║
        ║   → Output: ProcessingResult                   ║
        ╚═════════════════════════════════════════════════╝
                            │
                  ┌─────────┴──────────────────┐
                  │ ProcessingResult           │
                  │ ─────────────────────────  │
                  │ document_id: uuid          │
                  │ box_file_id: "12345"       │
                  │ destination_folder:        │
                  │   "/Invoices/2026/May/"    │
                  │ status: "success"          │
                  │ task_id: "task_789"        │
                  │ assigned_to:               │
                  │   "finance@company.com"    │
                  │ metadata_applied: {...}    │
                  │ notification_sent_to:      │
                  │   ["slack", "email"]       │
                  └─────────┬──────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    ╔═════════╗        ╔═════════╗         ╔═══════════╗
    ║  SLACK  ║        │  EMAIL  │         │ BOX FILE  │
    ║         ║        │         │         │ METADATA  │
    ║ Finance │        │Finance  │         │ + TAGS    │
    ║ team    ║        │Manager  │         │ + TASK    │
    ║ notified║        │ review  │         │ + EXT.    │
    ╚═════════╝        ╚═════════╝         ╚═══════════╝
                                                 │
                                                 ▼
                            ╔════════════════════════════════╗
                            ║ BOX UI EXTENSION (SIDEBAR)    ║
                            ║                                ║
                            ║ Shows classification result:   ║
                            ║ ✅ Invoice (95% confident)    ║
                            ║                                ║
                            ║ • Document Type: Invoice       ║
                            ║ • Confidence: 95%              ║
                            ║ • Vendor: Acme Corp           ║
                            ║ • Amount: $5,000               ║
                            ║ • Due Date: 2024-06-15        ║
                            ║                                ║
                            ║ [Assign Review Task] button    ║
                            ╚════════════════════════════════╝
                                        │
                                        ▼
                            User clicks "Assign Review Task"
                            → Finance manager gets Box task
                            → Task marked complete when done
```

---

## Timeline per Document

```
T+0:00    Email sent
          ↓
T+0:05    SendGrid webhook received
          ↓ Domain 1
T+0:10    Email parsed, attachments extracted
          ↓
T+0:15    IngestedDocument created
          ↓ Domain 2
T+0:20    LLM classifies document (Cerebras)
          ↓
T+0:25    ClassificationResult created
          ↓ Domain 3
T+0:30    File uploaded to Box with metadata
          ↓
T+0:35    Task created in Box
          ↓
T+0:40    Notifications sent (Slack + Email)
          ↓
T+0:45    Box UI Extension shows result
          ↓
T+1:00    User reviews in Box sidebar
          ↓
T+24:00   Finance manager completes task

Total end-to-end: <3 seconds for processing
```

---

## Domain Responsibilities

### Domain 1: Email Ingestion
**Input:** Email from SendGrid webhook
```json
{
  "to": ["system@boxsmartinbox.com"],
  "from": "bob@acme.com",
  "subject": "Invoice #12345",
  "attachments": [
    {
      "filename": "invoice.pdf",
      "type": "application/pdf"
    }
  ]
}
```

**Output:** IngestedDocument
```json
{
  "id": "doc-uuid-1234",
  "filename": "invoice.pdf",
  "content": "Invoice from Acme Corp...\nAmount: $5,000...",
  "content_type": "application/pdf",
  "uploaded_at": "2024-05-29T14:32:10Z",
  "source": "email",
  "email_from": "bob@acme.com",
  "file_size_bytes": 150000
}
```

---

### Domain 2: AI Classification
**Input:** IngestedDocument (from Domain 1)

**Processing:**
```
1. Prepare system prompt: "You are an invoice classifier..."
2. Extract first 10k chars from content
3. Call LLM with document text
4. Parse JSON response
5. Validate confidence is 0.0-1.0
6. Validate doc_type is in: invoice|contract|resume|receipt|id_document|purchase_order|other
7. Determine required_reviewer based on doc_type
```

**Output:** ClassificationResult
```json
{
  "document_id": "doc-uuid-1234",
  "doc_type": "invoice",
  "confidence": 0.95,
  "reasoning": "Document contains invoice header, line items, and total amount. Format typical of business invoice.",
  "extracted_fields": {
    "vendor": "Acme Corp",
    "amount": 5000,
    "date": "2024-05-29",
    "invoice_number": "INV-2024-1234"
  },
  "required_reviewer": "finance",
  "metadata_tags": [
    "vendor:acme",
    "q2_2026",
    "urgent"
  ],
  "classified_at": "2024-05-29T14:32:15Z"
}
```

---

### Domain 3: Box Integration
**Input:** ClassificationResult (from Domain 2)

**Processing:**
```
1. Route to destination folder:
   invoice → /Invoices/YYYY/Month/
   contract → /Contracts/YYYY/
   resume → /Resumes/
   
2. Upload file to Box folder
3. Get or create folder structure if needed
4. Apply metadata tags to file
5. Create task in Box:
   - Assigned to: finance manager
   - Title: "Review: Invoice from Acme Corp"
   - Priority: Based on confidence
6. Send notifications:
   - Slack: #finance channel
   - Email: finance@company.com
```

**Output:** ProcessingResult
```json
{
  "document_id": "doc-uuid-1234",
  "box_file_id": "file-567890",
  "destination_folder": "/Invoices/2026/May/",
  "status": "success",
  "task_id": "task-999",
  "assigned_to": "finance-manager@company.com",
  "metadata_applied": {
    "doc_type": "invoice",
    "confidence": 0.95,
    "vendor": "Acme Corp",
    "amount": 5000
  },
  "notification_sent_to": ["slack", "email"],
  "error_message": null,
  "completed_at": "2024-05-29T14:32:40Z"
}
```

---

## Box UI Extension Flow

### When User Opens File in Box:

```
1. User opens file in Box
2. Extension loads in sidebar
3. Extension calls: GET /documents/{file_id}
4. Backend returns ClassificationResult + ProcessingResult
5. UI displays:
   ✅ Document Type: INVOICE
   📊 Confidence: 95%
   👤 Reviewer: Finance Team
   📋 Fields: Vendor, Amount, Date
6. User can click "Assign Review Task" button
7. Task is created/updated in Box
```

### Extension → Backend Communication:

```
GET  /health                      Check backend is alive
GET  /documents/{document_id}     Get classification for file
POST /tasks/create                Create new review task
GET  /status                      Get processing statistics
```

---

## Real-World Example

### Scenario: Finance Department Receipt

```
Day 1, 2:30 PM: John from Finance forwards email with receipt:
  From: john@company.com
  To: system@boxsmartinbox.com
  Subject: Expense receipt - Lunch meeting
  Attachment: receipt.pdf ($47.50 lunch at The Grill)

↓ (Milliseconds later)

Backend processes:
1. Email extracted
2. LLM identifies as "receipt" (89% confidence)
3. Extracted: vendor="The Grill", amount=$47.50, date="May 29, 2024"
4. Assigned to "procurement" for verification
5. File moved to /Receipts/2026/May/
6. Task created: "Review Receipt: The Grill - $47.50"
7. Slack notified: "#procurement: New receipt needs review"

↓ (3 seconds total)

Day 1, 2:30:03 PM: Procurement Manager:
  Opens Box, sees new file with metadata
  Clicks Box sidebar → Sees classification result
  Assigns task to herself
  Approves expense

Result: Expense processed 95% automatically!
```

---

## Fallback & Error Handling

### If LLM Fails:
```
ClassificationResult.status = "escalated"
error_message = "Could not classify with confidence >80%"
→ Routes to manual review queue
→ Sends to compliance@company.com
→ Task marked as "Urgent Review Required"
```

### If Box Upload Fails:
```
ProcessingResult.status = "failure"
error_message = "Box API returned 401: Invalid credentials"
→ Document stored in quarantine folder
→ PagerDuty alert sent
→ Retry logic kicks in
```

### If Email Parser Fails:
```
IngestedDocument not created
EmailIngestionError raised
→ 400 response to SendGrid
→ SendGrid retries 10 times
→ If still failing: logged in dead letter queue
```

---

## Performance Targets

| Metric | Target | How Achieved |
|--------|--------|--------------|
| Email to Webhook | <1s | SendGrid handles |
| Ingestion | <1s | Direct parse, no DB |
| Classification | <2s | LLM API (Cerebras) |
| Box Integration | <1s | Box SDK, minimal ops |
| **Total E2E** | **<3s** | Async chain |

---

## Extensions Beyond Hackathon

### Phase 2: Advanced Features
- WebSocket real-time updates
- Batch processing (async queue)
- PDF OCR for scanned documents
- Multi-language support
- Custom classifier fine-tuning

### Phase 3: Production Grade
- PostgreSQL persistence
- Redis caching
- Webhook retry logic
- Dead letter queue
- Audit trail database
- Rate limiting
- RBAC

---

## Testing Your System

```bash
# Test endpoint chain:
1. Send test email to system@boxsmartinbox.com
2. Check backend logs for Domain 1 processing
3. Verify ClassificationResult in logs
4. Check Box for file in correct folder
5. Verify metadata applied
6. Confirm task created
7. Check Slack notification

# Or use curl:
curl http://localhost:8000/health
curl -X POST http://localhost:8000/documents/intake \
  -H "Content-Type: application/json" \
  -d @sample_invoice.json
```

---
