# Domain 3 Setup - Box Integration (Person C)

Welcome! You're implementing the **Box integration system** that routes and manages classified documents.

---

## Your Mission

**Input:** `ClassificationResult` from Domain 2 (classified document metadata)  
**Output:** `ProcessingResult` with file location, metadata, tasks, and notifications  
**Time Estimate:** 4-5 hours (most complex domain)

---

## What You're Building

```
ClassificationResult (from Domain 2)
    ↓
Your Code (Domain 3)
    ├─ Route to correct Box folder (/Invoices/2024/May/, etc.)
    ├─ Upload file to Box
    ├─ Apply metadata tags
    ├─ Create review task
    ├─ Assign to reviewer
    ├─ Send Slack notification
    ├─ Send email notification
    └─ Return ProcessingResult
    ↓
API Response + Notifications
```

---

## Files You Own

```
backend/domain_3_box_integration/
├── service.py             ← TODO: Implement Box orchestration
├── box_client.py          ← Already done (Box SDK wrapper)
├── metadata.py            ← Already done (metadata management)
├── tasks.py               ← Already done (task creation)
├── notifications.py       ← Already done (Slack/email)
└── tests/
    └── test_service.py    ← Already done (but YOU make it pass)
```

**Other files (DON'T MODIFY):**
- `backend/shared/types.py` (ClassificationResult input, ProcessingResult output)
- `backend/shared/config.py` (FOLDER_MAPPING, REVIEWER_MAPPING)

---

## Step 1: Understand the Requirements

### What is ProcessingResult? (Your Output)
```python
@dataclass
class ProcessingResult:
    document_id: str                # Reference to IngestedDocument.id
    box_file_id: str                # Box file ID (from Box API)
    destination_folder: str         # "/Invoices/2024/May/" (actual path)
    status: str                     # "success" | "failure" | "escalated"
    task_id: str | None             # Box task ID if created
    assigned_to: str | None         # Reviewer email
    metadata_applied: dict          # {"doc_type": "invoice", "confidence": 0.95, ...}
    notification_sent_to: list      # ["slack", "email"]
    error_message: str | None       # Error if status="failure"
    completed_at: datetime          # When completed
```

### Folder Structure (Use This Mapping!)
```python
FOLDER_MAPPING = {
    "invoice": "/Invoices/{year}/{month}/",
    "contract": "/Contracts/{year}/",
    "resume": "/Resumes/",
    "receipt": "/Receipts/{year}/{month}/",
    "id_document": "/ID_Documents/",
    "purchase_order": "/Purchases/{year}/",
    "other": "/Misc/"
}
```

Replace `{year}` with 2024, `{month}` with May, etc.

### Reviewer to Email Mapping
```python
REVIEWER_MAPPING = {
    "finance": "finance@company.com",
    "legal": "legal@company.com",
    "hr": "hr@company.com",
    "procurement": "procurement@company.com",
    None: None
}
```

---

## Step 2: Understand the Sub-Services

You DON'T need to implement these (already done!), but you need to use them:

### BoxClient (in `box_client.py`)
```python
from backend.domain_3_box_integration.box_client import BoxClient

client = BoxClient()

# Upload file
file_id = await client.upload_file(
    file_path="/path/to/invoice.pdf",
    folder_id="folder_123"
)

# Get or create folder
folder_id = await client.get_or_create_folder(
    path="/Invoices/2024/May/"
)

# Apply metadata
await client.apply_metadata(
    file_id="file_123",
    metadata={
        "doc_type": "invoice",
        "confidence": 0.95,
        "vendor": "Acme Corp"
    }
)
```

### MetadataManager (in `metadata.py`)
```python
from backend.domain_3_box_integration.metadata import MetadataManager

manager = MetadataManager()

# Format metadata from classification
metadata = manager.format_metadata(classification_result)
# Returns: {"doc_type": "invoice", "confidence": 0.95, ...}
```

### TaskManager (in `tasks.py`)
```python
from backend.domain_3_box_integration.tasks import TaskManager

task_manager = TaskManager(box_client)

# Create task
task_id = await task_manager.create_task(
    file_id="file_123",
    assigned_to="finance@company.com",
    message="Please review this invoice",
    due_date="2024-06-15"
)
```

### NotificationManager (in `notifications.py`)
```python
from backend.domain_3_box_integration.notifications import NotificationManager

notif_manager = NotificationManager()

# Send notifications
channels = await notif_manager.send(
    recipient="finance@company.com",
    doc_type="invoice",
    document_id="doc_123",
    confidence=0.95
)
# Returns: ["slack", "email"] (what was sent)
```

---

## Step 3: Look at the TODO Comments

**In `service.py`, line 24-46:**
```python
async def process(self, classification_result: ClassificationResult) -> ProcessingResult:
    """
    TODO: Implement end-to-end processing:
    1. Get or create destination folder using FOLDER_MAPPING
    2. Move file to correct folder
    3. Apply metadata from classification
    4. Create review task with assigned reviewer
    5. Send notifications (Slack + Email)
    6. Return ProcessingResult with all details
    7. Handle errors gracefully (escalate if needed)
    """
    raise NotImplementedError("TODO: Implement end-to-end Box processing")
```

---

## Step 4: Implementation Checklist

### Phase 1: Folder Routing (1 hour)
- [ ] In `service.py`, implement `process()`:
  - [ ] Get `doc_type` from classification_result
  - [ ] Look up folder path in FOLDER_MAPPING
  - [ ] Replace {year} with current year, {month} with current month
  - [ ] Call `self.box_client.get_or_create_folder(path)`
  - [ ] Get back `folder_id`

### Phase 2: File Upload (1 hour)
- [ ] Still in `process()`:
  - [ ] Get file from somewhere (Domain 1 sent it, it's in a temp location?)
  - [ ] Call `self.box_client.upload_file(file_path, folder_id)`
  - [ ] Get back `box_file_id`
  - [ ] Store it for later

### Phase 3: Metadata Application (1 hour)
- [ ] Still in `process()`:
  - [ ] Call `self.metadata_manager.format_metadata(classification_result)`
  - [ ] Get formatted metadata dict
  - [ ] Call `self.box_client.apply_metadata(box_file_id, metadata)`
  - [ ] Metadata is now on the file in Box

### Phase 4: Task Creation (1 hour)
- [ ] Still in `process()`:
  - [ ] Get `required_reviewer` from classification_result
  - [ ] Look up reviewer email in REVIEWER_MAPPING
  - [ ] Call `self.task_manager.create_task(box_file_id, email, message, due_date)`
  - [ ] Get back `task_id`

### Phase 5: Notifications (1 hour)
- [ ] Still in `process()`:
  - [ ] Get reviewer email
  - [ ] Call `self.notification_manager.send(email, doc_type, document_id, confidence)`
  - [ ] Get back list of channels (["slack", "email"])
  - [ ] Store for ProcessingResult

### Phase 6: Return Result & Error Handling (30 min)
- [ ] Create `ProcessingResult` with:
  - [ ] `document_id` from classification
  - [ ] `box_file_id` from upload
  - [ ] `destination_folder` (the path you routed to)
  - [ ] `status="success"` if all good
  - [ ] `status="failure"` if any step fails
  - [ ] `status="escalated"` if confidence < 80% (high-value docs)
  - [ ] `task_id`, `assigned_to`, `notification_sent_to` from steps above
  - [ ] `completed_at` = now
- [ ] Handle errors gracefully (log, don't crash)
- [ ] Return result

### Phase 7: Testing (30 min)
- [ ] Make Domain 3 tests pass:
  ```bash
  pytest backend/domain_3_box_integration/tests/ -v
  ```

---

## Step 5: Important Notes

### Folder Path Format
Use ISO format for dates:
```python
from datetime import datetime

year = datetime.now().year      # 2024
month = datetime.now().strftime("%B")  # "May"

path = f"/Invoices/{year}/{month}/"
```

### File Location
⚠️ **Question for Manager (Mason):**
Where is the file that needs to be uploaded? Domain 1 extracts it, but you need to know where it's stored.

Options:
- [ ] File is in memory as bytes
- [ ] File is saved to temp disk
- [ ] File is already in Box (just need to move/tag it)

Ask Manager before implementing!

### Error Handling - Status Codes

| Situation | Status | Action |
|-----------|--------|--------|
| All steps succeed | `success` | Return ProcessingResult |
| Low confidence (<80%) | `escalated` | Assign to manager instead |
| API error | `failure` | Log error, return with error_message |
| Rate limit | `failure` | Return with error, can be retried |

### Task Assignment
```python
# If confidence is good, assign to reviewer
if classification_result.confidence >= 0.80:
    reviewer_email = REVIEWER_MAPPING[classification_result.required_reviewer]
else:
    # If low confidence, escalate to manager
    reviewer_email = "manager@company.com"
```

---

## Step 6: Testing Your Work

### Manual Testing (Hard - Requires Box Account)
```python
# Create test classification
from backend.shared.types import ClassificationResult

result = ClassificationResult(
    document_id="doc-123",
    doc_type="invoice",
    confidence=0.95,
    reasoning="Clear invoice",
    extracted_fields={"vendor": "Acme", "amount": 5000},
    required_reviewer="finance",
    metadata_tags=["vendor:acme"],
    classified_at=datetime.now()
)

# Process it
from backend.domain_3_box_integration.service import BoxIntegrationService

service = BoxIntegrationService()
processing = await service.process(result)

# Should see:
print(processing.status)           # "success"
print(processing.destination_folder)  # "/Invoices/2024/May/"
print(processing.box_file_id)      # "file_123"
```

### Unit Testing
```bash
# Run Domain 3 tests (mocked, no real Box calls)
pytest backend/domain_3_box_integration/tests/ -v

# Run specific test
pytest backend/domain_3_box_integration/tests/test_service.py -v
```

---

## Step 7: Hand Off to Demo/API

When your tests pass, the demo team will call your endpoint!

**What They Need:**
- [ ] `ProcessingResult` object with all fields populated
- [ ] Correct folder routing (invoice goes to /Invoices/, etc.)
- [ ] Metadata applied to files in Box
- [ ] Tasks created and assigned
- [ ] Notifications sent

**Example of Good Output:**
```python
ProcessingResult(
    document_id="doc-uuid-123",
    box_file_id="file-567890",
    destination_folder="/Invoices/2024/May/",
    status="success",
    task_id="task-999",
    assigned_to="finance@company.com",
    metadata_applied={
        "doc_type": "invoice",
        "confidence": 0.95,
        "vendor": "Acme Corp",
        "amount": 5000
    },
    notification_sent_to=["slack", "email"],
    error_message=None,
    completed_at=datetime.now()
)
```

---

## Helpful Resources

**In the repo:**
- `backend/domain_3_box_integration/box_client.py` - Box SDK methods
- `backend/domain_3_box_integration/metadata.py` - Metadata formatting
- `backend/domain_3_box_integration/tasks.py` - Task creation
- `backend/domain_3_box_integration/notifications.py` - Notifications
- `backend/shared/config.py` - FOLDER_MAPPING, REVIEWER_MAPPING
- `backend/shared/types.py` - ProcessingResult definition
- `AGENT_DOMAIN_3_BOX.md` - Detailed domain guide

**External:**
- Box Python SDK: https://github.com/box/box-python-sdk
- Box API Docs: https://developer.box.com/reference

---

## Troubleshooting

**Box authentication failing?**
1. Check BOX_CLIENT_ID, SECRET in .env
2. Verify Box developer token hasn't expired
3. Try a simple health check first

**File upload failing?**
1. Check file path exists
2. Check Box folder exists
3. Check file size is reasonable

**Task creation failing?**
1. Check reviewer email is valid
2. Check Box has permission to create tasks
3. Try manually in Box first

**Tests failing?**
1. Check fixtures in `backend/shared/fixtures.py`
2. Make sure you're returning `ProcessingResult`, not dict
3. Look at test error - should tell you what's wrong

---

## Success Criteria

Your domain is **DONE** when:

- [ ] `pytest backend/domain_3_box_integration/tests/ -v` shows all passing ✅
- [ ] Files route to correct folders
- [ ] Metadata is applied to files
- [ ] Tasks are created and assigned
- [ ] Notifications send (Slack + email)
- [ ] ProcessingResult has all fields populated
- [ ] Error handling works (failures return status="failure")
- [ ] Low-confidence docs are escalated
- [ ] No `NotImplementedError` anywhere in your code

---

## Time Management

```
Hour 0-1:   Read this, understand requirements
Hour 1-2:   Implement folder routing + upload
Hour 2-3:   Implement metadata + tasks
Hour 3-4:   Implement notifications + error handling
Hour 4-5:   Write tests, make them pass
Hour 5-5.5: Celebrate! You're done! 🎉
```

This is the most complex domain. Take your time. Ask for help from Manager/Team.

---

**You've got this! Go build! 🚀**

Questions? Ask Mason (Manager), the team, or check CRISIS_RUNBOOK.md
