# Agent Domain 1: Email Ingestion

**For:** Person A (Email Ingestion)  
**Estimated Time:** 3-4 hours  
**Critical Success:** Return `IngestedDocument` with full text content from emails

---

## Your Mission

Accept emails from SendGrid webhook → Extract attachments and content → Return structured `IngestedDocument` object.

Nothing more, nothing less. You're not responsible for classification or Box integration.

## Your Files

You own everything in `backend/domain_1_email/`:

```
domain_1_email/
├── __init__.py           (Already created)
├── routes.py             (TODO: Webhook endpoint)
├── models.py             (Complete: EmailPayload, EmailAttachment)
├── service.py            (TODO: Email extraction logic)
└── tests/
    ├── __init__.py       (Already created)
    ├── test_routes.py    (TODO: Webhook tests)
    └── test_service.py   (TODO: Service tests)
```

**DO NOT EDIT:**
- `backend/domain_2_classifier/` (Person B's domain)
- `backend/domain_3_box_integration/` (Person C's domain)
- `backend/main.py` (PO's file)
- `backend/shared/types.py` (LOCKED contract)

## Input: Email from SendGrid

SendGrid webhook sends:
```
POST /webhooks/email HTTP/1.1
Content-Type: multipart/form-data

from: vendor@acme.com
to: inbox@yourcompany.com
subject: Invoice for Project X
text: Invoice details...
html: <html>Invoice details</html>
attachment1: [PDF file bytes]
attachment2: [PDF file bytes]
```

## Output: IngestedDocument

You must return this object:

```python
from backend.shared.types import IngestedDocument

IngestedDocument(
    id="550e8400-e29b-41d4-a716-446655440000",  # Auto-generated UUID
    filename="ACME_Invoice_2024.pdf",            # From attachment name
    content="Full text content here...",          # THIS IS CRITICAL - must be complete
    content_type="application/pdf",               # MIME type (pdf, text, image, html)
    uploaded_at=datetime.now(),                   # When uploaded
    source="email",                               # Always "email" for you
    email_from="vendor@acme.com",                 # Sender email
    file_size_bytes=45230,                        # Size in bytes
)
```

**Most Critical:** `content` field must contain the FULL text of the document.
- For PDFs: Extract text via PDF parser or OCR
- For images: Use OCR (Tesseract, Pytesseract)
- For text attachments: Just read the file
- Include email subject and body text too

## Implementation Roadmap

### Step 1: Implement routes.py (30 min)

```python
# POST /webhooks/email endpoint

from fastapi import APIRouter, Request
from backend.domain_1_email.models import WebhookResponse

router = APIRouter(prefix="/webhooks", tags=["email"])

@router.post("/email", response_model=WebhookResponse)
async def handle_email_webhook(request: Request):
    """
    TODO:
    1. Parse multipart/form-data from request
    2. Validate SendGrid signature (use service method)
    3. Extract email fields: from, to, subject, text, html, attachments
    4. Call email_service.ingest_email()
    5. Return {"status": "success", "document_id": "..."}
    """
    pass
```

**Test:** Use curl or Postman:
```bash
curl -X POST http://localhost:8000/webhooks/email \
  -H "Content-Type: application/json" \
  -d '{"from":"test@example.com","subject":"Test"}'
```

### Step 2: Implement service.py (2-3 hours)

Core business logic for email processing:

```python
# domain_1_email/service.py

class EmailIngestionService:
    
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
        TODO:
        1. Choose content: prefer text_content over html_content
        2. For attachments:
           a. Check file type (PDF, image, doc)
           b. Extract text:
              - PDF: Use PyPDF2 or pdfplumber
              - Image: Use OCR (pytesseract)
              - DOC: Use python-docx
           c. Combine with email text
        3. Validate file size < 25MB
        4. Create and return IngestedDocument
        5. Handle errors: raise EmailIngestionError
        """
        pass
    
    async def validate_sendgrid_signature(
        self,
        signature: str,
        timestamp: str,
        payload: str,
    ) -> bool:
        """
        TODO:
        1. Get SENDGRID_VERIFY_TOKEN from Config
        2. Combine: timestamp + payload + token
        3. Generate HMAC-SHA256 hash
        4. Compare with provided signature
        5. Return True/False
        """
        pass
```

### Step 3: Add Tests (30-45 min)

```python
# domain_1_email/tests/test_service.py

@pytest.mark.asyncio
async def test_ingest_email_plain_text():
    service = EmailIngestionService()
    result = await service.ingest_email(
        from_email="test@example.com",
        to_email="inbox@company.com",
        subject="Test Email",
        text_content="This is the email body",
        attachments=None
    )
    
    assert isinstance(result, IngestedDocument)
    assert result.content == "This is the email body"
    assert result.content_type == "text/plain"

@pytest.mark.asyncio
async def test_ingest_email_with_pdf():
    service = EmailIngestionService()
    # Create mock PDF
    result = await service.ingest_email(
        from_email="vendor@acme.com",
        to_email="inbox@company.com",
        subject="Invoice",
        text_content="",
        attachments=[...]  # Mock PDF bytes
    )
    
    assert result.content_type == "application/pdf"
    assert "Invoice" in result.content  # PDF text extracted
```

## Dependencies You'll Need

Add these to requirements.txt (already included):

- `fastapi` - Web framework
- `pydantic` - Models and validation
- `sendgrid` - Email parsing helper
- `PyPDF2` or `pdfplumber` - PDF text extraction
- `pytesseract` + `tesseract-ocr` - Image OCR
- `python-docx` - Word document parsing

## Testing Before Handoff

```bash
# Run only your tests
pytest domain_1_email/ -v

# Verify no cross-domain imports
grep -r "from backend.domain_" domain_1_email/
# Should return: 0 matches

# Check your code doesn't break anything
pytest -v
```

## Common Pitfalls & Solutions

### Pitfall 1: Empty Content Field
**Symptom:** `content = ""`  
**Problem:** PDF/image text extraction not working  
**Solution:** Use Pytesseract for images, PyPDF2 for PDFs:
```python
import PyPDF2
with open("invoice.pdf", "rb") as f:
    reader = PyPDF2.PdfReader(f)
    text = "".join([page.extract_text() for page in reader.pages])
```

### Pitfall 2: Signature Validation Failing
**Symptom:** All webhooks rejected as invalid  
**Problem:** Wrong hash algorithm or token  
**Solution:** Check SendGrid documentation:
```python
import hmac
import hashlib
signature = hmac.new(
    VERIFY_TOKEN.encode(),
    (timestamp + payload).encode(),
    hashlib.sha256
).hexdigest()
```

### Pitfall 3: Attachment Extraction Crashes
**Symptom:** Server crashes when processing email with attachments  
**Problem:** Malformed file or encoding issue  
**Solution:** Add try/except:
```python
try:
    text = extract_pdf_text(file_bytes)
except Exception as e:
    logger.warning(f"Failed to extract PDF: {e}")
    text = "[Could not extract PDF text]"
```

## Inputs You Depend On

- ✅ SendGrid API key working
- ✅ ngrok tunnel running (for webhooks)
- ✅ `shared/types.py` (provided, LOCKED)
- ✅ `shared/fixtures.py` with test emails (provided)

## Outputs You Provide

- `IngestedDocument` object with:
  - ✅ Unique ID (UUID)
  - ✅ Filename
  - ✅ **Full text content** (most important!)
  - ✅ Content type (detected)
  - ✅ Sender email
  - ✅ File size

Domain 2 depends on your `content` field being complete. If it's empty or truncated, classification will fail.

## Success Checklist

- [ ] POST /webhooks/email endpoint responding to requests
- [ ] Email signature validation working (or disabled for demo mode)
- [ ] Attachments being extracted from emails
- [ ] PDF text extraction working (returns readable text)
- [ ] Image OCR working (extracts text from images)
- [ ] IngestedDocument being returned with all fields
- [ ] domain_1_email tests passing: `pytest domain_1_email/ -v`
- [ ] No cross-domain imports: `grep "from backend.domain_" domain_1_email/`
- [ ] Ready to pass to Domain 2

## What's Next (Not Your Job)

- Domain 2 will call your `IngestedDocument` and classify it
- Domain 3 will move files to Box based on classification
- You don't need to worry about classification accuracy or Box integration

Just make sure your output is solid and complete. You're Person A's foundation for everything else.

---

## Quick Reference

**Your workflow:**
1. `routes.py` - FastAPI endpoint that receives emails
2. `service.py` - Business logic to extract and parse emails
3. `tests/` - Unit tests for your functions
4. `models.py` - Already complete, just use it

**Key files (read-only):**
- `backend/shared/types.py` - Your output schema (LOCKED)
- `backend/shared/config.py` - Environment variables
- `backend/shared/fixtures.py` - Sample test data

**Your contract:**
- **Input:** Raw email from SendGrid webhook
- **Output:** Fully-populated `IngestedDocument`
- **Success Metric:** Next domain can classify your documents

---

Good luck! Your work is the foundation everything builds on. 🚀
