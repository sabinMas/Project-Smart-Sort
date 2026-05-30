# API Reference

## Domain 1: Email Ingestion

### POST /webhooks/email
Receive and process incoming emails from SendGrid.

**Request** (multipart/form-data from SendGrid)
```
from: sender@example.com
to: inbox@yourcompany.com
subject: Invoice from ACME Corp
text: Email body text
html: <html>Email HTML</html>
attachment1: [binary file]
attachment2: [binary file]
```

**Response** (200 OK)
```json
{
  "status": "success",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Email processed successfully"
}
```

**Error Response** (400 Bad Request)
```json
{
  "status": "error",
  "document_id": null,
  "message": "Failed to extract attachments: file size exceeds 25MB"
}
```

### GET /webhooks/email/health
Health check for email ingestion service.

**Response** (200 OK)
```json
{
  "status": "ok",
  "service": "email-ingestion"
}
```

---

## Domain 2: AI Classification (Internal)

Called by main.py, not exposed directly to clients.

### classify(IngestedDocument) → ClassificationResult

**Internal Usage**
```python
from backend.domain_2_classifier.service import ClassificationService

service = ClassificationService()
result = await service.classify(ingested_document)
```

**Returns**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "doc_type": "invoice",
  "confidence": 0.98,
  "reasoning": "Contains invoice header, itemized services, total amount, and payment terms.",
  "extracted_fields": {
    "vendor": "ACME Corporation",
    "amount": 5000.00,
    "invoice_number": "INV-2024-05-001",
    "date": "2024-05-15"
  },
  "required_reviewer": "finance",
  "metadata_tags": ["vendor:acme", "amount:5000", "q2_2024"],
  "classified_at": "2024-05-22T10:31:00"
}
```

---

## Domain 3: Box Integration (Internal)

Called by main.py, not exposed directly to clients.

### process(ClassificationResult) → ProcessingResult

**Internal Usage**
```python
from backend.domain_3_box_integration.service import BoxIntegrationService

service = BoxIntegrationService()
result = await service.process(classification_result)
```

**Returns**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "box_file_id": "file_123456789",
  "destination_folder": "/Invoices/2024/May",
  "status": "success",
  "task_id": "task_987654321",
  "assigned_to": "finance@company.com",
  "metadata_applied": {
    "document_type": "invoice",
    "vendor": "ACME Corporation",
    "amount": "5000.00",
    "confidence": "0.98"
  },
  "notification_sent_to": ["slack", "email"],
  "error_message": null,
  "completed_at": "2024-05-22T10:35:00"
}
```

---

## Main Orchestration APIs

### POST /documents/intake
End-to-end document processing.

**Request**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "invoice.pdf",
  "content": "Full document text...",
  "content_type": "application/pdf",
  "uploaded_at": "2024-05-22T10:30:00",
  "source": "email",
  "email_from": "vendor@acme.com",
  "file_size_bytes": 45230
}
```

**Response** (200 OK)
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "box_file_id": "file_123456789",
  "destination_folder": "/Invoices/2024/May",
  "status": "success",
  "task_id": "task_987654321",
  "assigned_to": "finance@company.com",
  "metadata_applied": {
    "document_type": "invoice",
    "confidence": "0.98"
  },
  "notification_sent_to": ["slack", "email"],
  "error_message": null,
  "completed_at": "2024-05-22T10:35:00"
}
```

**Error Response** (400/500)
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "box_file_id": "",
  "destination_folder": "",
  "status": "failure",
  "task_id": null,
  "assigned_to": null,
  "metadata_applied": {},
  "notification_sent_to": [],
  "error_message": "LLM API timeout after 30 seconds",
  "completed_at": "2024-05-22T10:40:00"
}
```

### GET /status
System status and processing statistics.

**Response** (200 OK)
```json
{
  "status": "operational",
  "documents_processed": 42,
  "success_rate": "95.2%",
  "recent_documents": [
    {
      "document_id": "550e8400...",
      "status": "success",
      "doc_type": "invoice"
    },
    {
      "document_id": "660e8400...",
      "status": "success",
      "doc_type": "contract"
    }
  ]
}
```

### GET /documents/{document_id}
Get status of a specific document.

**Parameters**
- `document_id` (string, required): Document UUID

**Response** (200 OK)
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "box_file_id": "file_123456789",
  "destination_folder": "/Invoices/2024/May",
  "status": "success",
  "task_id": "task_987654321",
  "assigned_to": "finance@company.com",
  "metadata_applied": {...},
  "notification_sent_to": ["slack", "email"],
  "error_message": null,
  "completed_at": "2024-05-22T10:35:00"
}
```

**Error Response** (404 Not Found)
```json
{
  "detail": "Document 550e8400... not found"
}
```

### GET /health
System health check.

**Response** (200 OK)
```json
{
  "status": "ok",
  "service": "box-smart-inbox",
  "environment": "development"
}
```

---

## Document Types

Supported document types for classification:

| Type | Folder | Reviewer | Examples |
|------|--------|----------|----------|
| invoice | /Invoices | finance | Bills, invoices, statements |
| contract | /Contracts | legal | Agreements, contracts, NDAs |
| resume | /Resumes | hr | CVs, resumes, applications |
| receipt | /Receipts | finance | Receipts, order confirmations |
| id_document | /ID Documents | hr | Driver's license, passport, IDs |
| purchase_order | /Purchase Orders | procurement | POs, purchase requests |
| other | /Other Documents | none | Unclassified documents |

---

## Error Codes

| Status | Code | Meaning |
|--------|------|---------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input or validation error |
| 401 | Unauthorized | Authentication failed |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error during processing |
| 503 | Service Unavailable | Dependent service (LLM, Box) unavailable |

---

## Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get processing status
curl http://localhost:8000/status

# Check specific document
curl http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000
```

### Using Python

```python
import requests
import json

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Process document
document = {
    "filename": "invoice.pdf",
    "content": "Invoice details...",
    "content_type": "application/pdf",
    "source": "email"
}
response = requests.post("http://localhost:8000/documents/intake", json=document)
print(json.dumps(response.json(), indent=2))
```

---

See [Architecture](ARCHITECTURE.md) for system design details.
