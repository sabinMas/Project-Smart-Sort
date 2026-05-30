"""
Demo trigger script - simulates an email arriving with a PDF attachment.

Usage:
    py trigger_demo.py                          # Uses built-in sample invoice
    py trigger_demo.py invoice.pdf              # Use a real PDF file
    py trigger_demo.py contract.pdf contract    # Specify type hint in subject
    py trigger_demo.py --local                  # Target local backend

This bypasses SendGrid entirely and POSTs directly to the webhook.
Perfect for demos where email setup isn't configured.
"""

import sys
import base64
import json
import urllib.request
import urllib.error
import os

# ─── CONFIG ───────────────────────────────────────────────────────────────────
PRODUCTION_URL = "https://project-smart-sort.onrender.com"
LOCAL_URL      = "http://localhost:8000"
# ──────────────────────────────────────────────────────────────────────────────

# Minimal real PDF bytes (a valid 1-page PDF with text)
# This is a real PDF that Textract / pdfplumber can parse
SAMPLE_PDF_BASE64 = (
    "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2Jq"
    "CjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPJ4KZW5kb2Jq"
    "CjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIg"
    "NzkyXQovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4g"
    "Pj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyMDAgPj4Kc3RyZWFtCkJUCi9GMSAxMiBU"
    "ZgoxMDAgNzAwIFRkCihJTlZPSUNFKSBUagowIDAtMjAgVGQKKEZyb206IEFDTUUgQ29ycG9yYXRp"
    "b24pIFRqCjAgLTIwIFRkCihJbnZvaWNlICMgSU5WLTIwMjYtMDAxKSBUagowIC0yMCBUZAooRGF0"
    "ZTogTWF5IDMwLCAyMDI2KSBUagowIC0yMCBUZAooQW1vdW50OiAkMTUsMDAwLjAwKSBUagowIC0y"
    "MCBUZAooU2VydmljZXM6IFNvZnR3YXJlIERldmVsb3BtZW50IC0gUTIgMjAyNikgVGoKRVQKZW5k"
    "c3RyZWFtCmVuZG9iago1IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFz"
    "ZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAow"
    "MDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjMgMDAwMDAgbiAKMDAwMDAwMDEyMyAwMDAwMCBu"
    "IAAKMDAwMDAwMDI3NiAwMDAwMCBuIAAKMDAwMDAwMDUzMCAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9T"
    "aXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjYwOAolJUVPRgo="
)

SAMPLE_DOCS = {
    "invoice": {
        "subject": "Invoice from ACME Corporation - May 2026",
        "filename": "invoice_acme_may2026.pdf",
        "from":     "billing@acme-corp.com",
        "body":     "Please find attached Invoice #INV-2026-001 for $15,000.00 for software development services rendered in Q2 2026.",
    },
    "contract": {
        "subject": "Service Agreement - TechVendor Inc Q2 2026",
        "filename": "contract_techvendor_q2.pdf",
        "from":     "legal@techvendor.com",
        "body":     "Please review and sign the attached service agreement for $50,000 annual contract.",
    },
    "receipt": {
        "subject": "Receipt - Office Supplies Purchase",
        "filename": "receipt_officemax_may2026.pdf",
        "from":     "receipts@officemax.com",
        "body":     "Your receipt for office supplies totaling $234.50.",
    },
    "resume": {
        "subject": "Job Application - Senior Developer",
        "filename": "resume_john_doe.pdf",
        "from":     "john.doe@email.com",
        "body":     "Please find my resume attached for the Senior Developer position.",
    },
    "purchase_order": {
        "subject": "Purchase Order #PO-2026-042 - Equipment",
        "filename": "po_equipment_2026.pdf",
        "from":     "procurement@company.com",
        "body":     "Purchase Order for office equipment totaling $8,500.",
    },
}


def load_pdf(path: str) -> str:
    """Load a real PDF file and return base64 encoded string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_payload(doc_type: str, pdf_b64: str) -> dict:
    """Build the email webhook payload."""
    doc = SAMPLE_DOCS.get(doc_type, SAMPLE_DOCS["invoice"])
    return {
        "from": doc["from"],
        "to": "inbox@project-smart-sort.com",
        "subject": doc["subject"],
        "text": doc["body"],
        "attachments": [
            {
                "filename": doc["filename"],
                "content_type": "application/pdf",
                "content": pdf_b64,
            }
        ],
    }


def post_to_webhook(payload: dict, base_url: str) -> dict:
    """POST payload to webhook and return response."""
    url = f"{base_url}/webhooks/email"
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP {e.code}: {body}")
        raise
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}")
        print(f"Is the backend running at {base_url}?")
        raise


def print_result(result: dict):
    """Print the pipeline result nicely."""
    print("\n" + "="*60)
    print("PIPELINE RESULT")
    print("="*60)

    status = result.get("status", "unknown")
    symbol = "SUCCESS" if status == "success" else "PARTIAL" if "partial" in status else "FAILED"
    print(f"Status: {symbol} ({status})")
    print(f"Document ID: {result.get('document_id', 'N/A')}")
    print(f"Filename: {result.get('filename', 'N/A')}")

    pipeline = result.get("pipeline", {})
    if pipeline:
        print("\nPIPELINE STAGES:")
        print(f"  Domain 1 (Ingest):     {pipeline.get('domain_1_ingestion', '?')}")

        d2 = pipeline.get("domain_2_classification", {})
        print(f"  Domain 2 (Classify):   {d2.get('status', '?')}")
        if d2.get("type"):
            print(f"    -> Type: {d2['type']}")

        d3 = pipeline.get("domain_3_box_routing", {})
        print(f"  Domain 3 (Box Route):  {d3.get('status', '?')}")
        if d3.get("destination"):
            print(f"    -> Folder: {d3['destination']}")
        if d3.get("task_id"):
            print(f"    -> Task ID: {d3['task_id']}")
        if d3.get("assigned_to"):
            print(f"    -> Assigned to: {d3['assigned_to']}")

    pr = result.get("processing_result", {})
    if pr and pr.get("box_file_id"):
        print(f"\nBOX FILE ID: {pr['box_file_id']}")
        print(f"CHECK BOX: https://app.box.com")
        print(f"LOOK IN: {pr.get('destination_folder', '?')}")

    print("="*60 + "\n")


def main():
    args = sys.argv[1:]

    # Check for --local flag
    use_local = "--local" in args
    args = [a for a in args if a != "--local"]
    base_url = LOCAL_URL if use_local else PRODUCTION_URL

    # Determine doc type and PDF source
    pdf_path = None
    doc_type = "invoice"

    if args:
        if os.path.isfile(args[0]):
            pdf_path = args[0]
            # Guess doc type from filename
            name = args[0].lower()
            for t in SAMPLE_DOCS:
                if t in name:
                    doc_type = t
                    break
            # Allow explicit override
            if len(args) > 1 and args[1] in SAMPLE_DOCS:
                doc_type = args[1]
        elif args[0] in SAMPLE_DOCS:
            doc_type = args[0]

    # Load PDF
    if pdf_path:
        print(f"Loading PDF: {pdf_path}")
        pdf_b64 = load_pdf(pdf_path)
    else:
        print(f"Using built-in sample PDF ({doc_type})")
        pdf_b64 = SAMPLE_PDF_BASE64

    # Build and send payload
    payload = build_payload(doc_type, pdf_b64)
    doc = SAMPLE_DOCS[doc_type]

    print(f"\nTriggering pipeline on: {base_url}")
    print(f"Document type: {doc_type.upper()}")
    print(f"From: {doc['from']}")
    print(f"Subject: {doc['subject']}")
    print("Sending...\n")

    result = post_to_webhook(payload, base_url)
    print_result(result)

    return result


if __name__ == "__main__":
    main()
