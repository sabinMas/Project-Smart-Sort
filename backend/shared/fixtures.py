"""Pre-generated test fixtures for all domains."""

from datetime import datetime
from backend.shared.types import IngestedDocument, ClassificationResult, ProcessingResult

# ============================================
# Domain 1: IngestedDocument Fixtures
# ============================================

MOCK_INGESTED_DOCUMENT_INVOICE = IngestedDocument(
    id="doc-invoice-001",
    filename="ACME_Invoice_2024_05.pdf",
    content="""INVOICE

From: ACME Corporation
123 Main Street
New York, NY 10001

To: Your Company
456 Oak Avenue
Los Angeles, CA 90001

Invoice #: INV-2024-05-001
Date: May 15, 2024
Due Date: June 15, 2024

Description: Professional Services
Amount: $5,000.00

Total Due: $5,000.00

Thank you for your business!""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 5, 22, 10, 30, 0),
    source="email",
    email_from="invoices@acme.com",
    file_size_bytes=45230,
)

MOCK_INGESTED_DOCUMENT_CONTRACT = IngestedDocument(
    id="doc-contract-001",
    filename="Service_Agreement_2024.pdf",
    content="""SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of May 15, 2024, by and between:

PROVIDER: ABC Services Inc.
CLIENT: Your Organization

1. SERVICES
Provider agrees to provide the following services:
- Consulting services
- Project management
- Technical support

2. TERM
This agreement shall commence on June 1, 2024 and continue for 12 months.

3. COMPENSATION
Client shall pay Provider $50,000 annually.

4. CONFIDENTIALITY
Both parties agree to maintain confidentiality of sensitive information.

5. TERMINATION
Either party may terminate with 30 days notice.

Signed,
ABC Services Inc.""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 5, 22, 11, 15, 0),
    source="email",
    email_from="legal@abcservices.com",
    file_size_bytes=67890,
)

MOCK_INGESTED_DOCUMENT_RESUME = IngestedDocument(
    id="doc-resume-001",
    filename="John_Doe_Resume.pdf",
    content="""JOHN DOE
john.doe@email.com | (555) 123-4567

OBJECTIVE
Seeking a Senior Software Engineer position in a dynamic tech company.

EXPERIENCE
Senior Software Engineer | Tech Corp | 2021 - Present
- Led team of 5 engineers
- Implemented microservices architecture
- Improved API performance by 40%

Software Engineer | StartUp Inc | 2019 - 2021
- Developed full-stack applications
- Mentored junior developers

EDUCATION
Bachelor of Science in Computer Science
State University, 2019

SKILLS
Python, JavaScript, Go, AWS, Docker, Kubernetes""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 5, 22, 14, 45, 0),
    source="email",
    email_from="jobs@candidate.com",
    file_size_bytes=23456,
)

MOCK_INGESTED_DOCUMENT_EMAIL = IngestedDocument(
    id="doc-email-001",
    filename="Email_Receipt_2024.txt",
    content="""From: vendor@supplier.com
To: purchasing@company.com
Date: May 20, 2024
Subject: Receipt for Order #PO-2024-1234

Hi,

Thank you for your order. Here are the receipt details:

Order Number: PO-2024-1234
Date: May 18, 2024
Items: Office Supplies

Subtotal: $1,250.00
Tax: $100.00
Total: $1,350.00

Payment Method: Credit Card ending in 4242

Expected Delivery: May 25, 2024

Best regards,
Supplier Team""",
    content_type="text/plain",
    uploaded_at=datetime(2024, 5, 22, 9, 0, 0),
    source="email",
    email_from="vendor@supplier.com",
    file_size_bytes=456,
)

MOCK_INGESTED_DOCUMENT_RECEIPT = IngestedDocument(
    id="doc-receipt-001",
    filename="Receipt_Coffee_Shop.jpg",
    content="[Image of receipt from Local Coffee Shop dated May 22, 2024, Total: $7.50]",
    content_type="image/jpeg",
    uploaded_at=datetime(2024, 5, 22, 15, 30, 0),
    source="box_file_request",
    email_from=None,
    file_size_bytes=156789,
)

# ============================================
# Domain 2: ClassificationResult Fixtures
# ============================================

MOCK_CLASSIFICATION_INVOICE = ClassificationResult(
    document_id="doc-invoice-001",
    doc_type="invoice",
    confidence=0.98,
    reasoning="Document contains invoice header, itemized services, total amount, and payment terms typical of business invoices.",
    extracted_fields={
        "vendor": "ACME Corporation",
        "amount": 5000.00,
        "currency": "USD",
        "invoice_number": "INV-2024-05-001",
        "date": "2024-05-15",
        "due_date": "2024-06-15",
    },
    required_reviewer="finance",
    metadata_tags=["vendor:acme", "amount:5000", "q2_2024", "invoice"],
    classified_at=datetime(2024, 5, 22, 10, 31, 0),
)

MOCK_CLASSIFICATION_CONTRACT = ClassificationResult(
    document_id="doc-contract-001",
    doc_type="contract",
    confidence=0.95,
    reasoning="Document contains service agreement with parties, terms, conditions, compensation, and signature blocks typical of legal contracts.",
    extracted_fields={
        "contract_type": "Service Agreement",
        "parties": ["ABC Services Inc.", "Your Organization"],
        "effective_date": "2024-06-01",
        "contract_value": 50000.00,
        "term_months": 12,
    },
    required_reviewer="legal",
    metadata_tags=["contract", "services", "annual:50000", "12_months"],
    classified_at=datetime(2024, 5, 22, 11, 16, 0),
)

MOCK_CLASSIFICATION_RESUME = ClassificationResult(
    document_id="doc-resume-001",
    doc_type="resume",
    confidence=0.99,
    reasoning="Document contains structured resume with header, objective, experience, education, and skills section.",
    extracted_fields={
        "candidate_name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "(555) 123-4567",
        "years_experience": 5,
        "education": "Bachelor of Science in Computer Science",
        "current_position": "Senior Software Engineer",
    },
    required_reviewer="hr",
    metadata_tags=["resume", "senior_engineer", "5_years_experience"],
    classified_at=datetime(2024, 5, 22, 14, 46, 0),
)

MOCK_CLASSIFICATION_RECEIPT = ClassificationResult(
    document_id="doc-receipt-001",
    doc_type="receipt",
    confidence=0.92,
    reasoning="Document shows itemized expenses with business name, items, amounts, and date typical of transaction receipts.",
    extracted_fields={
        "vendor": "Local Coffee Shop",
        "amount": 7.50,
        "currency": "USD",
        "date": "2024-05-22",
        "items": ["Coffee", "Pastry"],
    },
    required_reviewer="finance",
    metadata_tags=["receipt", "expense:7.50", "food_beverage"],
    classified_at=datetime(2024, 5, 22, 15, 31, 0),
)

# ============================================
# Domain 3: ProcessingResult Fixtures
# ============================================

MOCK_PROCESSING_SUCCESS = ProcessingResult(
    document_id="doc-invoice-001",
    box_file_id="file_123456789",
    destination_folder="/Invoices/2024/May",
    status="success",
    task_id="task_987654321",
    assigned_to="finance@company.com",
    metadata_applied={
        "document_type": "invoice",
        "vendor": "ACME Corporation",
        "amount": "5000",
        "confidence": "0.98",
    },
    notification_sent_to=["slack", "email"],
    error_message=None,
    completed_at=datetime(2024, 5, 22, 10, 35, 0),
)

MOCK_PROCESSING_FAILURE = ProcessingResult(
    document_id="doc-unknown-001",
    box_file_id="",
    destination_folder="",
    status="failure",
    task_id=None,
    assigned_to=None,
    metadata_applied={},
    notification_sent_to=[],
    error_message="Failed to classify document: LLM provider error",
    completed_at=datetime(2024, 5, 22, 10, 40, 0),
)

MOCK_PROCESSING_ESCALATED = ProcessingResult(
    document_id="doc-contract-001",
    box_file_id="file_987654321",
    destination_folder="/Contracts/2024",
    status="escalated",
    task_id="task_111111111",
    assigned_to="legal_manager@company.com",
    metadata_applied={
        "document_type": "contract",
        "confidence": "0.95",
        "requires_review": "true",
    },
    notification_sent_to=["slack"],
    error_message="High-value contract requires legal team review",
    completed_at=datetime(2024, 5, 22, 11, 20, 0),
)
