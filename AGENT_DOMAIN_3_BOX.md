# Agent Domain 3: Box Integration

**For:** Person C (Box Integration)  
**Estimated Time:** 4-5 hours (most complex)  
**Critical Success:** File correctly placed in Box, task assigned to right reviewer, notifications sent

---

## Your Mission

Accept `ClassificationResult` from Domain 2 → Move file to correct Box folder → Apply metadata → Create review task → Send notifications → Return `ProcessingResult`.

You're connecting everything to Box. Make sure documents reach the right place with the right context.

## Your Files

You own everything in `backend/domain_3_box_integration/`:

```
domain_3_box_integration/
├── __init__.py           (Already created)
├── box_client.py         (TODO: Box SDK wrapper)
├── metadata.py           (TODO: Apply metadata to files)
├── tasks.py              (TODO: Create and assign tasks)
├── notifications.py      (TODO: Send Slack/email)
├── service.py            (TODO: Orchestration)
└── tests/
    ├── __init__.py       (Already created)
    └── test_service.py   (TODO: Integration tests)
```

**DO NOT EDIT:**
- `backend/domain_1_email/` (Person A's domain)
- `backend/domain_2_classifier/` (Person B's domain)
- `backend/main.py` (PO's file)
- `backend/shared/types.py` (LOCKED contract)

## Input: ClassificationResult

From Domain 2 (Person B):

```python
ClassificationResult(
    document_id="550e8400-e29b-41d4-a716-446655440000",
    doc_type="invoice",  # One of 7 types
    confidence=0.98,
    reasoning="Contains invoice details...",
    extracted_fields={
        "vendor": "ACME Corporation",
        "amount": 5000.00,
        "invoice_number": "INV-2024-05-001",
        "date": "2024-05-15",
    },
    required_reviewer="finance",
    metadata_tags=["vendor:acme", "q2_2024"],
    classified_at=datetime(...),
)
```

## Output: ProcessingResult

You must return this object:

```python
from backend.shared.types import ProcessingResult

ProcessingResult(
    document_id="550e8400-e29b-41d4-a716-446655440000",  # From input
    box_file_id="file_123456789",  # ID in Box
    destination_folder="/Invoices/2024/May",  # Where file went
    status="success",  # success, failure, or escalated
    task_id="task_987654321",  # Box task ID
    assigned_to="finance@company.com",  # Assigned reviewer email
    metadata_applied={
        "document_type": "invoice",
        "confidence": "0.98",
        "vendor": "ACME Corporation",
    },
    notification_sent_to=["slack", "email"],  # Channels notified
    error_message=None,  # Error details if failed
    completed_at=datetime.now(),
)
```

**Most Critical:**
- `box_file_id` must be valid
- `destination_folder` must match doc_type
- `status` must be "success" or explain failure
- `assigned_to` must be correct reviewer

## Routing Rules

Use `FOLDER_MAPPING` and `REVIEWER_MAPPING` from `backend/shared/config.py`:

```python
FOLDER_MAPPING = {
    "invoice": "/Invoices",
    "contract": "/Contracts",
    "resume": "/Resumes",
    "receipt": "/Receipts",
    "id_document": "/ID Documents",
    "purchase_order": "/Purchase Orders",
    "other": "/Other Documents",
}

REVIEWER_MAPPING = {
    "invoice": "finance",
    "contract": "legal",
    "resume": "hr",
    "receipt": "finance",
    "id_document": "hr",
    "purchase_order": "procurement",
    "other": None,
}
```

Full folder structure:
```
/Invoices/2024/May/
/Contracts/2024/
/Resumes/
/Receipts/
/ID Documents/
/Purchase Orders/
/Other Documents/
```

## Implementation Roadmap

### Step 1: Implement box_client.py (1 hour)

Box SDK wrapper for API operations:

```python
# domain_3_box_integration/box_client.py

from box_sdk_gen import Client
from box_sdk_gen.auth import OAuth2

class BoxClient:
    def __init__(self):
        """
        TODO:
        1. Create OAuth2 auth using BOX_CLIENT_ID and BOX_CLIENT_SECRET
        2. Initialize box-sdk-gen Client
        3. Test connection with enterprise ID
        4. Raise BoxAuthenticationError if auth fails
        """
        self.client = None
    
    async def upload_file(
        self,
        file_path: str,
        folder_id: str,
        file_name: str,
    ) -> str:
        """
        Upload file to Box folder.
        
        TODO:
        1. Read file from local path
        2. Upload to folder_id with file_name
        3. Return Box file ID
        """
        pass
    
    async def move_file(
        self,
        file_id: str,
        destination_folder_id: str,
    ) -> str:
        """
        Move file to different Box folder.
        
        TODO:
        1. Update file's parent folder
        2. Return updated file ID
        """
        pass
    
    async def get_or_create_folder(self, folder_path: str) -> str:
        """
        Get or create folder at path like "/Invoices/2024/May".
        
        TODO:
        1. Parse path: split by "/"
        2. Create folders if needed
        3. Return final folder ID
        """
        pass
```

### Step 2: Implement metadata.py (45 min)

Apply metadata to Box files:

```python
# domain_3_box_integration/metadata.py

class MetadataManager:
    async def apply_metadata(
        self,
        file_id: str,
        metadata: Dict[str, Any],
        template_name: str = "box_smart_inbox_metadata",
    ) -> bool:
        """
        Apply metadata template to file.
        
        TODO:
        1. Validate metadata against template
        2. Use Box metadata API
        3. Return True/False
        4. Raise MetadataApplicationError on failure
        """
        pass
    
    def build_metadata_dict(self, classification_result) -> Dict[str, Any]:
        """Build metadata from classification result"""
        return {
            "document_type": classification_result.doc_type,
            "confidence": str(classification_result.confidence),
            "vendor": classification_result.extracted_fields.get("vendor", ""),
            "amount": str(classification_result.extracted_fields.get("amount", "")),
            "tags": ", ".join(classification_result.metadata_tags),
        }
```

### Step 3: Implement tasks.py (45 min)

Create and assign review tasks:

```python
# domain_3_box_integration/tasks.py

class TaskManager:
    def __init__(self, box_client):
        self.box_client = box_client
    
    async def create_review_task(
        self,
        file_id: str,
        doc_type: str,
        assigned_to_email: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> str:
        """
        Create review task on file.
        
        TODO:
        1. Map doc_type to reviewer role (finance, legal, hr, procurement)
        2. Create Box task on file_id
        3. Set task message
        4. Assign to reviewer
        5. Return task ID
        """
        pass
    
    async def assign_task(
        self,
        task_id: str,
        assigned_to_email: str,
    ) -> bool:
        """Assign task to user by email"""
        pass
```

### Step 4: Implement notifications.py (45 min)

Send Slack and email notifications:

```python
# domain_3_box_integration/notifications.py

class NotificationManager:
    async def send_notifications(
        self,
        document_id: str,
        doc_type: str,
        assigned_to_email: str,
        channels: List[str] = None,
    ) -> List[str]:
        """
        Send notifications to channels.
        
        TODO:
        1. If "slack": POST to SLACK_WEBHOOK_URL
        2. If "email": Send via SMTP or SendGrid
        3. Return list of successful channels
        """
        pass
    
    async def _send_slack_notification(
        self,
        document_id: str,
        doc_type: str,
        assigned_to_email: str,
    ) -> bool:
        """
        Send Slack message.
        
        TODO:
        1. Format message with document details
        2. POST to Config.SLACK_WEBHOOK_URL
        3. Return True if successful
        """
        pass
    
    async def _send_email_notification(
        self,
        document_id: str,
        assigned_to_email: str,
    ) -> bool:
        """
        Send email notification.
        
        TODO:
        1. Compose email with review link
        2. Send via SMTP/SendGrid
        3. Return True if successful
        """
        pass
```

### Step 5: Implement service.py (2 hours)

Orchestrate everything:

```python
# domain_3_box_integration/service.py

class BoxIntegrationService:
    def __init__(self):
        self.box_client = BoxClient()
        self.metadata_manager = MetadataManager()
        self.task_manager = TaskManager(self.box_client)
        self.notification_manager = NotificationManager()
    
    async def process(self, classification_result: ClassificationResult) -> ProcessingResult:
        """
        End-to-end Box integration.
        
        TODO:
        1. Get destination folder from doc_type
        2. Get or create folder structure
        3. Move file there
        4. Apply metadata
        5. Create and assign task
        6. Send notifications
        7. Return ProcessingResult
        8. Handle errors gracefully (escalate if needed)
        """
        try:
            # Step 1: Route to destination
            folder_path = FOLDER_MAPPING[classification_result.doc_type]
            folder_id = await self._move_to_destination_folder(
                file_id,
                classification_result.doc_type
            )
            
            # Step 2: Apply metadata
            metadata = await self._apply_metadata(file_id, classification_result)
            
            # Step 3: Create task
            task_id, reviewer = await self._create_and_assign_task(
                file_id,
                classification_result.doc_type
            )
            
            # Step 4: Send notifications
            notified = await self.notification_manager.send_notifications(
                classification_result.document_id,
                classification_result.doc_type,
                reviewer,
                channels=["slack", "email"]
            )
            
            return ProcessingResult(
                document_id=classification_result.document_id,
                box_file_id=file_id,
                destination_folder=folder_path,
                status="success",
                task_id=task_id,
                assigned_to=reviewer,
                metadata_applied=metadata,
                notification_sent_to=notified,
                error_message=None,
                completed_at=datetime.now(),
            )
        except Exception as e:
            # Return failure result instead of crashing
            return ProcessingResult(
                document_id=classification_result.document_id,
                box_file_id="",
                destination_folder="",
                status="failure",
                error_message=str(e),
                completed_at=datetime.now(),
            )
```

### Step 6: Add Tests (30-45 min)

```python
# domain_3_box_integration/tests/test_service.py

@pytest.mark.asyncio
async def test_process_invoice():
    service = BoxIntegrationService()
    result = await service.process(MOCK_CLASSIFICATION_INVOICE)
    
    assert result.status == "success"
    assert result.box_file_id != ""
    assert "/Invoices" in result.destination_folder
    assert result.assigned_to == "finance"
    assert "slack" in result.notification_sent_to

@pytest.mark.asyncio
async def test_process_contract():
    service = BoxIntegrationService()
    result = await service.process(MOCK_CLASSIFICATION_CONTRACT)
    
    assert "/Contracts" in result.destination_folder
    assert result.assigned_to == "legal"
```

## Box SDK Basics

You'll use `box-sdk-gen`:

```python
from box_sdk_gen import Client
from box_sdk_gen.auth import OAuth2

# Auth
auth = OAuth2(
    client_id=Config.BOX_CLIENT_ID,
    client_secret=Config.BOX_CLIENT_SECRET,
)

# Create client
client = Client(auth=auth)

# Upload file
file = client.uploads.upload_file(
    request_body={
        "attributes": {
            "name": "invoice.pdf",
            "parent": {"id": folder_id}
        },
        "file": open("invoice.pdf", "rb")
    }
)

# Move file
client.files.update_file(
    file.id,
    request_body={
        "parent": {"id": new_folder_id}
    }
)

# Create folder
folder = client.folders.create_folder(
    request_body={
        "name": "Invoices",
        "parent": {"id": "0"}  # Root
    }
)
```

## Testing Before Handoff

```bash
# Run only your tests
pytest domain_3_box_integration/ -v

# Verify no cross-domain imports
grep -r "from backend.domain_" domain_3_box_integration/
# Should return: 0 matches

# Check nothing broke
pytest -v
```

## Common Pitfalls & Solutions

### Pitfall 1: Box Authentication Fails
**Symptom:** "Invalid Box credentials"  
**Problem:** Wrong API keys or enterprise ID  
**Solution:**
```python
print(Config.BOX_CLIENT_ID)  # Should print value
print(Config.BOX_ENTERPRISE_ID)
# Regenerate keys in Box admin console if needed
```

### Pitfall 2: File Upload Fails
**Symptom:** "Failed to upload file"  
**Problem:** File not found, permissions, size  
**Solution:**
```python
# Make sure file exists
assert os.path.exists(file_path)
# Check permissions in Box folder
# Check file size < Box limit
```

### Pitfall 3: Folder Structure Wrong
**Symptom:** File in "/Invoices" instead of "/Invoices/2024/May"  
**Problem:** Folder path creation logic broken  
**Solution:**
```python
# Test folder creation separately
folder_id = await box_client.get_or_create_folder("/Invoices/2024/May")
print(f"Created folder: {folder_id}")
```

### Pitfall 4: Task Assignment Fails
**Symptom:** "Invalid reviewer email"  
**Problem:** Email not in Box or permissions  
**Solution:**
```python
# Use enterprise user list
users = client.users.get_users()
valid_emails = [u.login for u in users]
assert reviewer_email in valid_emails
```

### Pitfall 5: Notification Not Sent
**Symptom:** Slack/email notification fails silently  
**Problem:** Invalid webhook URL or SMTP config  
**Solution:**
```python
# Test Slack webhook
import requests
requests.post(Config.SLACK_WEBHOOK_URL, json={"text": "Test"})
# Check if 200 response

# Test email
import smtplib
# Or use SendGrid API directly
```

## Inputs You Depend On

- ✅ `ClassificationResult` from Domain 2 (Person B)
- ✅ Box API credentials in `.env`
- ✅ SLACK_WEBHOOK_URL or email config in `.env`
- ✅ `shared/types.py` (provided, LOCKED)
- ✅ `shared/fixtures.py` with test data (provided)
- ✅ FOLDER_MAPPING and REVIEWER_MAPPING from config

## Outputs You Provide

- `ProcessingResult` with:
  - ✅ Valid `box_file_id`
  - ✅ Correct `destination_folder`
  - ✅ `status` success/failure
  - ✅ Assigned reviewer email
  - ✅ Notifications sent list

End users see this in logs and dashboard.

## Success Checklist

- [ ] Box authentication working
- [ ] Files uploading to Box successfully
- [ ] Folder routing working (invoices → /Invoices, contracts → /Contracts, etc.)
- [ ] Metadata applied to files
- [ ] Review tasks created and assigned
- [ ] Slack notifications working
- [ ] Email notifications working (if enabled)
- [ ] ProcessingResult returned with all fields
- [ ] domain_3_box_integration tests passing
- [ ] No cross-domain imports
- [ ] Error handling graceful (returns failure instead of crashing)

## What's Next (Not Your Job)

- PO will integrate everything in main.py
- Dashboard will display results
- Demo will show end-to-end flow

Your job is to make sure files reach Box correctly and people are notified.

---

## Quick Reference

**Your workflow:**
1. `box_client.py` - Wrapper around Box SDK
2. `metadata.py` - Apply metadata to files
3. `tasks.py` - Create review tasks
4. `notifications.py` - Send Slack/email
5. `service.py` - Orchestrate everything
6. `tests/` - Unit tests

**Key files (read-only):**
- `backend/shared/types.py` - Your output schema (LOCKED)
- `backend/shared/config.py` - FOLDER_MAPPING, REVIEWER_MAPPING, credentials
- `fixtures.py` - Sample classification results

**Your contract:**
- **Input:** `ClassificationResult` with doc_type and metadata
- **Output:** `ProcessingResult` showing file placed in Box with task assigned
- **Success Metric:** Document lands in right folder with right reviewer notified

---

You're the bridge between AI and Box. Make it smooth! 🌉
