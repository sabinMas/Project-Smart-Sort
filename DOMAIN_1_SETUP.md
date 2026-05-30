# Domain 1 Setup - Email Ingestion (Person A)

Welcome! You're implementing the **email ingestion system** that receives emails and extracts documents.

---

## Your Mission

**Input:** Email from SendGrid webhook (with attachments)  
**Output:** `IngestedDocument` object with full text content  
**Time Estimate:** 3-4 hours

---

## What You're Building

```
SendGrid Email
    ↓
Your Code (Domain 1)
    ├─ Parse email headers (from, to, subject)
    ├─ Extract email body (text or HTML)
    ├─ Download attachments (PDF, images, etc.)
    ├─ Extract text from attachments (OCR if needed)
    └─ Validate and return IngestedDocument
    ↓
Domain 2 gets IngestedDocument
```

---

## Files You Own

```
backend/domain_1_email/
├── routes.py              ← TODO: Implement webhook handler
├── service.py             ← TODO: Implement email processing logic
├── models.py              ← Already done (request/response models)
└── tests/
    ├── test_routes.py     ← Already done (but YOU make it pass)
    └── test_service.py    ← Already done (but YOU make it pass)
```

**Other files (DON'T MODIFY):**
- `backend/shared/types.py` (IngestedDocument - this is your OUTPUT type)
- `backend/shared/config.py` (configuration)
- `backend/shared/errors.py` (exception types)

---

## Step 1: Understand the Requirements

### What is IngestedDocument? (Your Output)
```python
@dataclass
class IngestedDocument:
    id: str                     # UUID (generate one)
    filename: str               # "invoice.pdf" or email subject
    content: str                # FULL TEXT - email body + extracted attachment text
    content_type: str           # "text/plain", "application/pdf", "image/jpeg"
    uploaded_at: datetime       # When it was ingested
    source: str                 # "email" (always for Domain 1)
    email_from: str | None      # "bob@acme.com"
    file_size_bytes: int | None # Size of attachment if available
```

### What SendGrid Sends
```json
{
  "from": "bob@acme.com",
  "to": "greenriver.hack.squad@gmail.com",
  "subject": "Invoice #12345",
  "text": "Please see attached",
  "html": "<html>...</html>",
  "attachments": [
    {
      "filename": "invoice.pdf",
      "content": "base64-encoded-file-content",
      "content_type": "application/pdf"
    }
  ]
}
```

---

## Step 2: Look at the TODO Comments

**In `routes.py`, line 19-41:**
```python
@router.post("/email", response_model=WebhookResponse)
async def handle_email_webhook(request: Request) -> WebhookResponse:
    """
    TODO: Implement webhook handler:
    1. Validate webhook signature (use email_service.validate_sendgrid_signature)
    2. Parse email payload (from/to/subject/attachments)
    3. Call email_service.ingest_email() to process
    4. On success: Return {"status": "success", "document_id": "..."}
    5. On error: Log error and return 400 with error message
    """
    raise NotImplementedError("TODO: Implement SendGrid webhook handler")
```

**In `service.py`, line 13-53:**
```python
async def ingest_email(
    self,
    from_email: str,
    to_email: str,
    subject: str,
    text_content: Optional[str] = None,
    html_content: Optional[str] = None,
    attachments: Optional[list] = None,
) -> IngestedDocument:
    """
    TODO: Implement email parsing logic:
    1. Extract email content (prefer text over HTML)
    2. For attachments:
       - Validate file type and size
       - Extract file content
       - For PDFs/images: Consider OCR if needed
    3. Create IngestedDocument with:
       - filename from subject or attachment name
       - content as full text + extracted attachment content
       - content_type based on attachment (pdf, image, text, etc.)
       - source="email"
       - email_from from sender
    4. Return IngestedDocument object
    """
    raise NotImplementedError("TODO: Implement email ingestion logic")
```

---

## Step 3: Implementation Checklist

### Phase 1: Basic Email Parsing (1 hour)
- [ ] In `service.py`, implement `ingest_email()`:
  - [ ] Accept email parameters
  - [ ] Prefer text_content over html_content
  - [ ] Combine subject + content into `content` field
  - [ ] Create IngestedDocument with basic fields
  - [ ] Return it

### Phase 2: Attachment Handling (1 hour)
- [ ] Still in `service.py`, add attachment processing:
  - [ ] Validate attachment types (PDF, images, text)
  - [ ] Validate file sizes (don't accept 100MB files)
  - [ ] Extract text from attachments:
    - [ ] For plain text: just decode
    - [ ] For PDFs: use a library (try `pdfplumber` or `pypdf`)
    - [ ] For images: skip for now (or try OCR with `pytesseract`)
  - [ ] Append extracted text to `content`
  - [ ] Set `content_type` based on attachment

### Phase 3: Webhook Handler (1 hour)
- [ ] In `routes.py`, implement `handle_email_webhook()`:
  - [ ] Get request body
  - [ ] Validate SendGrid signature using `email_service.validate_sendgrid_signature()`
  - [ ] Parse email fields
  - [ ] Call `email_service.ingest_email()`
  - [ ] Return `{"status": "success", "document_id": document.id}`
  - [ ] Return 400 on errors

### Phase 4: Signature Validation (30 min)
- [ ] In `service.py`, implement `validate_sendgrid_signature()`:
  - [ ] Get SENDGRID_VERIFY_TOKEN from config
  - [ ] Create HMAC-SHA256 hash of timestamp + payload
  - [ ] Compare with provided signature
  - [ ] Return True/False

### Phase 5: Testing (30 min)
- [ ] Make Domain 1 tests pass:
  ```bash
  pytest backend/domain_1_email/tests/ -v
  ```
- [ ] Both tests should pass:
  - [ ] `test_health_check` (already passing)
  - [ ] `test_ingest_email` (you'll make this pass)

---

## Step 4: Important Notes

### SendGrid Webhook Signature Validation
```python
import hmac
import hashlib

# SENDGRID_VERIFY_TOKEN from config
# signature from header: X-Twilio-Email-Event-Webhook-Signature
# timestamp from header: X-Twilio-Email-Event-Webhook-Timestamp

def validate(signature, timestamp, payload):
    key = SENDGRID_VERIFY_TOKEN.encode()
    message = timestamp + payload
    expected = hmac.new(key, message.encode(), hashlib.sha256).hexdigest()
    return signature == expected
```

### Text Extraction from PDFs
```python
# Option 1: pdfplumber (recommended)
import pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text()

# Option 2: pypdf
from PyPDF2 import PdfReader
reader = PdfReader("file.pdf")
text = "\n".join(page.extract_text() for page in reader.pages)
```

### Don't Go Overboard on OCR
For a hackathon, just support:
- ✅ Plain text files
- ✅ PDFs with embedded text
- ✅ Basic image support (if easy)
- ❌ Complex OCR (saves time for coding)

---

## Step 5: Testing Your Work

### Manual Testing
```bash
# Terminal 1: Start backend
uvicorn backend.main:app --reload

# Terminal 2: Send test email using curl
curl -X POST http://localhost:8000/webhooks/email \
  -H "Content-Type: application/json" \
  -d '{
    "from": "test@acme.com",
    "to": "greenriver.hack.squad@gmail.com",
    "subject": "Test Invoice",
    "text": "Invoice from Acme Corp for $5000",
    "attachments": []
  }'

# Expected response:
# {"status": "success", "document_id": "uuid-here"}
```

### Unit Testing
```bash
# Run Domain 1 tests
pytest backend/domain_1_email/tests/ -v

# Run specific test
pytest backend/domain_1_email/tests/test_service.py::test_ingest_email -v

# Run with coverage
pytest backend/domain_1_email/ --cov=backend.domain_1_email -v
```

---

## Step 6: Hand Off to Domain 2

When your tests pass, Domain 2 will use your `IngestedDocument` to classify.

**What Domain 2 Needs:**
- [ ] `content` field is FULL TEXT (email + attachments combined)
- [ ] `filename` is descriptive
- [ ] `content_type` is accurate
- [ ] `source` is "email"
- [ ] `email_from` is the sender's email

**Example of Good Output:**
```python
IngestedDocument(
    id="doc-uuid-123",
    filename="invoice.pdf",
    content="Invoice from Acme Corp\nPO Number: 12345\nAmount: $5000\nDate: May 29, 2024",
    content_type="application/pdf",
    source="email",
    email_from="bob@acme.com",
    uploaded_at=datetime.now(),
    file_size_bytes=150000
)
```

---

## Helpful Resources

**In the repo:**
- `backend/shared/types.py` - See IngestedDocument definition
- `backend/shared/config.py` - How to get SENDGRID_VERIFY_TOKEN
- `backend/shared/errors.py` - Custom exceptions to use
- `backend/shared/logging.py` - How to log
- `backend/shared/fixtures.py` - Test data helpers
- `AGENT_DOMAIN_1_EMAIL.md` - Detailed domain guide

**External:**
- SendGrid documentation: https://docs.sendgrid.com/for-developers/parsing/inbound-mail
- PDF extraction: https://github.com/jsvine/pdfplumber
- HMAC validation: https://docs.python.org/3/library/hmac.html

---

## Troubleshooting

**Tests failing?**
1. Make sure you implemented `ingest_email()`
2. Check that you're returning `IngestedDocument` (not a dict)
3. Look at `backend/shared/fixtures.py` for example data
4. Read the test failure message - it's usually helpful

**SendGrid signature validation failing?**
1. Double-check HMAC-SHA256 implementation
2. Make sure you're using the right token
3. Try without validation first, add it later

**Attachment extraction not working?**
1. Start simple: just handle text files
2. Add PDF support with pdfplumber
3. Skip images/OCR for hackathon (time saver!)

---

## Success Criteria

Your domain is **DONE** when:

- [ ] `pytest backend/domain_1_email/tests/ -v` shows all passing ✅
- [ ] Email webhook handler works (`/webhooks/email` endpoint)
- [ ] IngestedDocument has full text content extracted
- [ ] Attachments are parsed (at least text/PDF)
- [ ] Tests cover normal case + error cases
- [ ] No `NotImplementedError` anywhere in your code
- [ ] You can explain the flow to someone else

---

## Time Management

```
Hour 0-1:   Read this, understand requirements
Hour 1-2:   Implement basic ingest_email()
Hour 2-3:   Add attachment handling
Hour 3-4:   Implement webhook handler + signature validation
Hour 4-4.5: Write tests, make them pass
Hour 4.5-5: Celebrate! You're done! 🎉
```

Don't spend too much time on fancy features. Get the core working, then refine.

---

**You've got this! Go build! 🚀**

Questions? Ask the team on Discord/Slack or check CRISIS_RUNBOOK.md

