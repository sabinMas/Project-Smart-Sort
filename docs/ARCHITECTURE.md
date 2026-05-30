# Architecture Overview

## System Design

Box Smart Inbox is built on three independent vertical domains that communicate through locked type contracts.

```
┌─────────────────────────────────────────────────────────────┐
│                     Email/File Upload                       │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│  Domain 1: Email Ingestion (Person A)                       │
│  ├─ Receive email from SendGrid webhook                     │
│  ├─ Extract attachments & content                           │
│  └─ Return: IngestedDocument                                │
└────────────────────────────┬────────────────────────────────┘
                             │ IngestedDocument (locked contract)
┌────────────────────────────▼────────────────────────────────┐
│  Domain 2: AI Classification (Person B)                     │
│  ├─ Accept IngestedDocument                                 │
│  ├─ Call LLM (Cerebras Llama 3.1 8B)                        │
│  └─ Return: ClassificationResult                            │
└────────────────────────────┬────────────────────────────────┘
                             │ ClassificationResult (locked contract)
┌────────────────────────────▼────────────────────────────────┐
│  Domain 3: Box Integration (Person C)                       │
│  ├─ Accept ClassificationResult                             │
│  ├─ Move file to correct folder                             │
│  ├─ Apply metadata & create task                            │
│  ├─ Send notifications                                      │
│  └─ Return: ProcessingResult                                │
└────────────────────────────┬────────────────────────────────┘
                             │ ProcessingResult
                             ▼
                    Notifications & Dashboard
                  (Slack, Email, Status Page)
```

## Data Flow

### 1. Ingestion (Domain 1)

```
Email arrives
    ↓
SendGrid webhook → /webhooks/email
    ↓
[Extract email metadata]
  - From address
  - Subject
  - Body (text/html)
    ↓
[Process attachments]
  - Download files
  - Extract text (OCR for PDFs/images)
  - Validate size/type
    ↓
Create IngestedDocument
  - id: unique UUID
  - filename: from attachment or subject
  - content: full text (email + attachments)
  - content_type: detected MIME type
  - source: "email"
    ↓
Return to main.py
```

### 2. Classification (Domain 2)

```
IngestedDocument received
    ↓
[Call LLM]
  - System prompt: Classification instructions
  - User prompt: Document text (first 10k chars)
  - Model: Llama 3.1 8B via Cerebras
    ↓
[LLM Response (JSON)]
{
  "doc_type": "invoice|contract|resume|...",
  "confidence": 0.95,
  "reasoning": "...",
  "extracted_fields": {vendor, amount, date, ...},
  "required_reviewer": "finance|legal|hr|procurement|null",
  "metadata_tags": ["vendor:acme", "q2_2024", ...]
}
    ↓
[Validate response]
  - Confidence in [0.0, 1.0]
  - Doc_type valid
  - Required fields present
    ↓
Create ClassificationResult
    ↓
Return to main.py
```

### 3. Box Integration (Domain 3)

```
ClassificationResult received
    ↓
[Route to destination]
  invoice → /Invoices/YYYY/Month
  contract → /Contracts/YYYY
  resume → /Resumes/
  ...
    ↓
[Move file in Box]
  - Upload to correct folder
  - Get/create folder structure
    ↓
[Apply metadata]
  - Document type
  - Confidence score
  - Extracted fields (vendor, amount, etc.)
    ↓
[Create review task]
  - Map doc_type to reviewer (finance, legal, hr, procurement)
  - Assign task to reviewer
  - Set due date
    ↓
[Send notifications]
  - Slack: Brief summary
  - Email: Full details + review link
    ↓
Create ProcessingResult
  - status: success|failure|escalated
  - box_file_id
  - task_id
  - assigned_to
  - metadata_applied
    ↓
Return to main.py → Dashboard/API
```

## Type Contracts (LOCKED)

### IngestedDocument
**Output of Domain 1, Input to Domain 2**

```python
@dataclass
class IngestedDocument:
    id: str                    # UUID
    filename: str              # Original filename
    content: str               # Full text content (OCR'd if image/PDF)
    content_type: str          # MIME type
    uploaded_at: datetime      # When uploaded
    source: str                # "email" or "box_file_request"
    email_from: str | None     # Sender email
    file_size_bytes: int | None
```

### ClassificationResult
**Output of Domain 2, Input to Domain 3**

```python
@dataclass
class ClassificationResult:
    document_id: str                      # Reference to IngestedDocument.id
    doc_type: str                         # invoice|contract|resume|receipt|id_document|purchase_order|other
    confidence: float                     # 0.0 to 1.0
    reasoning: str                        # Why model chose this type
    extracted_fields: dict                # {vendor, amount, date, ...}
    required_reviewer: str | None         # finance|legal|hr|procurement|None
    metadata_tags: list[str]              # [vendor:acme, q2_2024, ...]
    classified_at: datetime
```

### ProcessingResult
**Output of Domain 3, sent to notifications/dashboard**

```python
@dataclass
class ProcessingResult:
    document_id: str
    box_file_id: str                      # ID of file in Box
    destination_folder: str                # /Invoices/2024/May
    status: str                            # success|failure|escalated
    task_id: str | None                   # Box task ID
    assigned_to: str | None                # Email of assigned reviewer
    metadata_applied: dict                # {doc_type, confidence, ...}
    notification_sent_to: list[str]       # [slack, email]
    error_message: str | None
    completed_at: datetime
```

## Domain Independence

### Critical Rules

1. **No Cross-Domain Imports**
   ```python
   # ✅ OK
   from backend.shared.types import IngestedDocument
   from backend.domain_1_email import service
   
   # ❌ NEVER
   from backend.domain_2_classifier import ClassificationService  # Domain 2 imports Domain 3
   from backend.domain_3_box_integration import BoxClient        # Domain 1 imports Domain 3
   ```

2. **Communication Through Types**
   - Domain 1 returns `IngestedDocument`
   - Domain 2 accepts `IngestedDocument`, returns `ClassificationResult`
   - Domain 3 accepts `ClassificationResult`, returns `ProcessingResult`
   - No passing of service objects or internal state

3. **Orchestration in main.py Only**
   ```python
   # main.py - The ONLY place where domains interact
   
   @app.post("/documents/intake")
   async def intake(document: IngestedDocument) -> ProcessingResult:
       # Domain 1 → Domain 2
       classification = await classification_service.classify(document)
       
       # Domain 2 → Domain 3
       result = await box_service.process(classification)
       
       return result
   ```

## Extension Points

Teams can add domain-specific models without modifying the type contracts:

```python
# Domain 1: Email-specific models
from backend.domain_1_email.models import EmailPayload, EmailAttachment

# Domain 2: Classification-specific models
from backend.domain_2_classifier.schemas import ClassificationResponse

# Domain 3: Box-specific models
# (None needed - use Box SDK types directly)
```

## Testing Strategy

```
┌─────────────────────────────────────┐
│     Unit Tests (Per Domain)         │
├─────────────────────────────────────┤
│ Domain 1: Test email parsing        │
│   - Mock Domain 2 responses         │
│   - Use fixtures for test emails    │
│                                     │
│ Domain 2: Test LLM classification   │
│   - Mock LLM responses              │
│   - Mock Box API calls              │
│   - Use fixtures for test docs      │
│                                     │
│ Domain 3: Test Box integration      │
│   - Mock Box API                    │
│   - Mock LLM responses              │
│   - Use fixtures for classifications│
│                                     │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   Integration Tests (main.py)       │
├─────────────────────────────────────┤
│ IngestedDoc → ClassificationResult  │
│           → ProcessingResult        │
│                                     │
│ Tests all domains together          │
│ Uses real service implementations   │
└─────────────────────────────────────┘
```

## Error Handling

Each domain reports errors through its output type:

```python
# Domain 1: Returns IngestedDocument (if successful) or raises EmailIngestionError
# Domain 2: Returns ClassificationResult (if successful) or raises ClassificationError
# Domain 3: Returns ProcessingResult with status="failure" and error_message
```

Domain 3 escalates high-confidence failures:
```python
ProcessingResult(
    status="escalated",
    error_message="High-value contract requires manual legal review",
    assigned_to="legal_manager@company.com"
)
```

## Scalability Notes

For future enhancements beyond hackathon:

1. **Async Queue** (Domain 1 → Domain 2)
   - Redis queue for document processing
   - Decouple ingestion from classification
   - Use `USE_ASYNC_QUEUE=true` in .env

2. **Database** (PostgreSQL)
   - Persist document state
   - Track processing history
   - Enable retry logic

3. **Webhook Retry** (Domain 3)
   - Box and notification failures
   - Exponential backoff
   - Dead letter queue

---

For more details, see:
- [API Reference](API_REFERENCE.md)
- [Team Guidelines](../TEAM_GUIDELINES.md)
