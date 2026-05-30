# Test Documents for Box Smart Inbox

This directory contains sample documents for testing the classification system.

## How to Generate PDFs

### Option 1: Use Online Tools (Fastest)
1. Copy content from the `.txt` files
2. Paste into Google Docs
3. Download as PDF
4. Place in this directory

### Option 2: Use LibreOffice (Local)
```bash
# On macOS
brew install libreoffice

# Convert .txt to PDF
libreoffice --headless --convert-to pdf sample_invoice.txt

# Move to test_documents folder
mv sample_invoice.pdf test_documents/
```

### Option 3: Use Python (Automated)
```bash
pip install reportlab

python generate_pdfs.py
```

## Sample Documents

### 1. Sample Invoice (`sample_invoice.pdf`)

**Purpose:** Test invoice classification
**Content includes:**
- Invoice header with date
- Vendor information
- Line items with amounts
- Total amount
- Payment terms
- Invoice number

**Expected Classification:**
- Type: `invoice`
- Confidence: 0.90+
- Extracted Fields: vendor, amount, date, invoice_number

**Use Case:** Finance team review

---

### 2. Sample Contract (`sample_contract.pdf`)

**Purpose:** Test contract classification
**Content includes:**
- Legal header
- Party information
- Effective date
- Key terms and conditions
- Signature blocks
- Date and signatures

**Expected Classification:**
- Type: `contract`
- Confidence: 0.85+
- Extracted Fields: parties, effective_date, key_terms

**Use Case:** Legal team review

---

### 3. Sample Receipt (`sample_receipt.pdf`)

**Purpose:** Test receipt classification
**Content includes:**
- Store/vendor name
- Transaction date
- Items purchased
- Prices
- Total amount
- Payment method
- Receipt number

**Expected Classification:**
- Type: `receipt`
- Confidence: 0.88+
- Extracted Fields: vendor, amount, date, items

**Use Case:** Expense management

---

### 4. Sample Resume (`sample_resume.pdf`)

**Purpose:** Test resume classification
**Content includes:**
- Candidate name and contact
- Professional summary
- Experience section
- Education section
- Skills section

**Expected Classification:**
- Type: `resume`
- Confidence: 0.92+
- Extracted Fields: name, email, phone, skills, education

**Use Case:** HR screening

---

### 5. Sample Purchase Order (`sample_po.pdf`)

**Purpose:** Test purchase order classification
**Content includes:**
- PO number
- Vendor information
- Order date
- Line items with quantities
- Unit prices
- Total amount
- Delivery address

**Expected Classification:**
- Type: `purchase_order`
- Confidence: 0.89+
- Extracted Fields: po_number, vendor, amount, delivery_date

**Use Case:** Procurement team

---

## Testing With These Documents

### Step 1: Email a Document
```bash
# Open Gmail
# Compose email to: system@boxsmartinbox.com
# Attach: sample_invoice.pdf
# Send
```

### Step 2: Check Backend Logs
```bash
# In backend terminal, should see:
# ✅ Domain 1: IngestedDocument created
# ✅ Domain 2: ClassificationResult - invoice, 0.95 confidence
# ✅ Domain 3: File moved to /Invoices/2026/May/
```

### Step 3: Verify in Box
```bash
# Open Box
# Navigate to correct folder (/Invoices, /Contracts, etc.)
# Check file has metadata applied
# Check task was created
```

### Step 4: View in Extension
```bash
# Open the file in Box
# Sidebar should show classification
# Confidence score displayed
# Can assign task from there
```

## Expected Results per Document Type

| Document | Folder | Reviewer | Confidence |
|----------|--------|----------|------------|
| Invoice | `/Invoices/2026/May/` | Finance | 90%+ |
| Contract | `/Contracts/2026/` | Legal | 85%+ |
| Receipt | `/Receipts/2026/May/` | Procurement | 88%+ |
| Resume | `/Resumes/` | HR | 92%+ |
| PO | `/Purchases/2026/` | Procurement | 89%+ |

## Demo Script

For the live demo:

1. **Prepare:** Have all 5 PDFs ready to email
2. **Send:** Pick the invoice, send it
3. **Monitor:** Show backend logs processing
4. **Show Result:** Display classification result
5. **Verify:** Open Box, show file in correct folder
6. **Extend:** Show the UI extension displaying the result

## Troubleshooting

### "PDF not recognized"
- Ensure PDFs are actual PDF files (not text with .pdf extension)
- Try re-downloading from Google Docs

### "Classification wrong"
- Check the document content matches what's expected
- LLM might have low confidence on poor quality scans
- Try with a cleaner copy

### "File not in correct folder"
- Check the doc_type classification
- Verify Domain 3 routing rules in code
- Check Box API permissions

## Creating Custom Documents

To add more test documents:

1. Create a `.txt` file with realistic content
2. Convert to PDF (using one of the methods above)
3. Update this README with the new document
4. Test with the system

Example:
```
# my_custom_document.txt
MEDICAL INVOICE

From: City Hospital
Date: May 29, 2024
Patient: John Doe

Procedure: CT Scan
Cost: $2,500

Patient Responsibility: $500 (after insurance)
Due Date: June 15, 2024
```

Then convert to PDF and email to test system.

## Best Practices

✅ **Good test documents:**
- Clear, readable text
- Realistic business content
- Complete information fields
- Professional formatting

❌ **Avoid:**
- Scanned images with poor OCR
- Incomplete documents
- Mixed/ambiguous content
- Extremely long documents (>50 pages)

## Integration with CI/CD

For automated testing:

```bash
# In .github/workflows/test.yml
- name: Test with sample documents
  run: |
    pytest backend/tests/test_integration.py -v
    # Uses mock PDFs, not actual files
```

## Performance Testing

Test classification speed with documents:

```bash
# Small file (50 KB)
time curl -X POST http://localhost:8000/documents/intake \
  -F "file=@sample_invoice.pdf"

# Expected: <3 seconds
```

## License & Usage

These documents are:
- ✅ Free to use for testing
- ✅ Unrealistic (simplified) for clarity
- ✅ Safe to include in git commits
- ✅ Useful for demos

Don't use for:
- ❌ Production data
- ❌ Personally identifiable information
- ❌ Real business documents
- ❌ Confidential information

---

**Ready to test? Email one to system@boxsmartinbox.com! 📧**
