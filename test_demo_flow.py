#!/usr/bin/env python
"""
Demo flow test script - Creates test classification data and tests end-to-end.
Run this to populate the system with demo data for the judges.

Usage:
    python test_demo_flow.py
"""

import asyncio
import json
from datetime import datetime
from backend.shared.types import ClassificationResult
from backend.domain_3_box_integration.approval_service import (
    _demo_documents,
    _demo_approvals,
)

# Sample test documents to classify
TEST_DOCUMENTS = [
    {
        "filename": "invoice_2026_05.pdf",
        "doc_type": "invoice",
        "confidence": 0.96,
        "vendor": "ACME Corporation",
        "amount": 15500.00,
        "reasoning": "Document header shows 'INVOICE', contains itemized charges, total due at bottom",
    },
    {
        "filename": "contract_q2_2026.pdf",
        "doc_type": "contract",
        "confidence": 0.92,
        "vendor": "TechVendor Inc",
        "amount": 50000.00,
        "reasoning": "Contains 'Agreement', signature blocks, legal terms, dated terms and conditions",
    },
    {
        "filename": "receipt_office_supplies.pdf",
        "doc_type": "receipt",
        "confidence": 0.88,
        "vendor": "OfficeMax",
        "amount": 234.50,
        "reasoning": "Receipt format with itemized list, total, payment method visible",
    },
]


def create_test_documents():
    """Create test classification results in demo mode."""
    print("\n📋 Creating test classification data...")
    print("-" * 60)

    for i, doc_info in enumerate(TEST_DOCUMENTS, 1):
        doc_id = f"demo_doc_{i:03d}"

        classification = ClassificationResult(
            document_id=doc_id,
            doc_type=doc_info["doc_type"],
            confidence=doc_info["confidence"],
            reasoning=doc_info["reasoning"],
            extracted_fields={
                "vendor": doc_info.get("vendor", ""),
                "amount": doc_info.get("amount", 0),
            },
            required_reviewer="finance" if doc_info["doc_type"] in ["invoice", "receipt"] else "legal",
            metadata_tags=[f"vendor:{doc_info.get('vendor', '').lower()}", "demo", "q2_2026"],
        )

        # Store in demo mode storage
        _demo_documents[doc_id] = {
            "filename": doc_info["filename"],
            "doc_type": classification.doc_type,
            "confidence": classification.confidence,
            "extracted_vendor": classification.extracted_fields.get("vendor"),
            "extracted_amount": classification.extracted_fields.get("amount"),
            "classification": classification.to_dict(),
            "created_at": datetime.utcnow().isoformat(),
            "status": "classified",
        }

        print(f"\n✅ {i}. {doc_info['filename']}")
        print(f"   Type: {classification.doc_type.upper()} (confidence: {classification.confidence:.0%})")
        print(f"   Vendor: {doc_info.get('vendor', 'N/A')}")
        print(f"   Amount: ${doc_info.get('amount', 0):,.2f}")
        print(f"   ID: {doc_id}")

    print("\n" + "-" * 60)
    print(f"✨ Created {len(TEST_DOCUMENTS)} test documents in demo mode")
    return list(_demo_documents.keys())


def show_api_test_commands(doc_ids):
    """Show curl commands to test the API."""
    print("\n\n🧪 TEST THE API WITH THESE COMMANDS:")
    print("=" * 60)

    print("\n1️⃣  Health check:")
    print("   curl http://localhost:8000/health | jq")

    print("\n2️⃣  Get system status:")
    print("   curl http://localhost:8000/status | jq")

    print("\n3️⃣  Get approval history for first document:")
    first_id = doc_ids[0]
    print(f"   curl http://localhost:8000/api/approvals/{first_id} | jq")

    print("\n4️⃣  Approve a document (ready for Box):")
    print(f"""   curl -X POST http://localhost:8000/api/approvals/review \\
     -H "Content-Type: application/json" \\
     -d '{{
       "document_id": "{first_id}",
       "action": "approve",
       "final_recipients": ["finance@company.com", "cfo@company.com"],
       "reason": "Approved for processing"
     }}' | jq""")

    print("\n" + "=" * 60)


def show_box_extension_info():
    """Show what the Box extension should display."""
    print("\n\n📦 BOX EXTENSION SHOULD DISPLAY:")
    print("=" * 60)
    print("""
When the Box extension loads for any of these files:
- Shows document type (INVOICE, CONTRACT, RECEIPT)
- Shows confidence percentage (88%-96%)
- Shows extracted vendor name
- Shows extracted amount
- Displays metadata tags
- Allow to create review task
    """)
    print("=" * 60)


def show_next_steps():
    """Show next steps for the demo."""
    print("\n\n🚀 NEXT STEPS FOR DEMO:")
    print("=" * 60)
    print("""
1. Start the backend:
   cd backend
   python -m uvicorn backend.main:app --reload

2. Run this script to populate demo data:
   python test_demo_flow.py

3. Open the Box extension UI locally:
   cd box-extension
   npm run dev
   # Visit http://localhost:5173

4. Test API calls (see commands above)

5. Verify the extension displays classification data

6. For judges: Deploy to Vercel and test in actual Box.com
    """)
    print("=" * 60)


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       BOX SMART INBOX - DEMO DATA GENERATOR                ║")
    print("╚════════════════════════════════════════════════════════════╝")

    doc_ids = create_test_documents()
    show_api_test_commands(doc_ids)
    show_box_extension_info()
    show_next_steps()

    print("\n✅ Demo data created! Run the test commands above to verify.\n")
