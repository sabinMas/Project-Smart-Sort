# 🚀 Box Smart Inbox - Team Tasks for Demo Day

## System Overview

Your system is **production-ready** with:
- ✅ Backend: Deployed to Render (https://project-smart-sort.onrender.com)
- ✅ Frontend: Deployed to Vercel (https://box-extension.vercel.app)
- ✅ Database: PostgreSQL on Render
- ✅ AWS Textract: Integrated with 1000 credits
- ✅ Playwright Demo: Automated recording script ready

**3 Independent Domains Working:**
1. **Domain 1** - Email ingestion + PDF parsing (Textract)
2. **Domain 2** - AI classification (Cerebras LLM)
3. **Domain 3** - Box routing + task creation

---

## 👤 Team Member #1: Email & Document Handler

### Your Role
Create realistic test scenarios by sending emails with PDF attachments to demonstrate the full document ingestion → classification → Box workflow.

### Why This Matters
- Judges want to see **real email documents** being processed
- Shows the complete system pipeline working end-to-end
- Demonstrates Textract extracting data from actual PDFs
- Builds credibility for a production system

---

## 📧 Task Set #1: Create Test Documents & Send Emails

### 1.1 Create 5 Sample PDF Documents
Create realistic business PDFs that showcase classification accuracy:

**Invoice (High-value)**
- Use: Template from Canva or Word
- Include: Vendor name (ACME Corp), Amount ($25,000), Invoice #, Dates
- Purpose: Test invoice detection (target: 95%+ confidence)
- Save as: `test_invoice_tech.pdf`

**Contract (Legal Document)**
- Use: Basic contract template (T&Cs or Service Agreement)
- Include: Company names, Terms, Effective date, Signature blocks
- Purpose: Test contract classification
- Save as: `test_contract_vendor.pdf`

**Receipt (Low-value)**
- Use: Receipt template from Canva or generate from browser
- Include: Store name (Office Depot), Items, Total amount, Date
- Purpose: Test receipt detection
- Save as: `test_receipt_supplies.pdf`

**Purchase Order (Procurement)**
- Use: PO template from Word
- Include: Vendor details, Line items, Total cost, PO number
- Purpose: Test PO classification
- Save as: `test_po_equipment.pdf`

**Resume (HR Document)**
- Use: Your own resume or template
- Include: Education, Experience, Skills, Contact info
- Purpose: Test HR document classification
- Save as: `test_resume_candidate.pdf`

### 1.2 Send Emails with Attachments (2-3 Each)

**Setup Instructions:**

1. **Configure your email:**
   ```
   SENDGRID_INBOUND_URL=https://your-ngrok-url.onrender.com/webhooks/email
   ```
   (Check your .env for this)

2. **Send 2-3 emails** with different PDFs:
   ```
   TO: inbox@yourdomain.com (or your Box email)
   SUBJECT: "Invoice from ACME Corporation - March 2026"
   ATTACHMENT: test_invoice_tech.pdf
   BODY: "Please review and approve this invoice"
   ```

3. **Repeat for each document type:**
   - Invoice email
   - Contract email
   - Receipt email
   - PO email
   - Resume email

**Why Multiple Emails:**
- Tests the system's ability to handle multiple documents
- Shows variety in classification results
- Demonstrates the full pipeline processing in real-time

### 1.3 Verify Textract is Extracting Data

Check the backend logs:
```
"Using Amazon Textract for test_invoice_tech.pdf"
"Successfully extracted X chars from test_invoice_tech.pdf"
```

This proves Textract is working on your actual PDFs!

### 1.4 Create "Bad Document" Test Cases (Bonus)

Optional but impressive:
- **Scanned image of a receipt** - Shows OCR via Textract
- **Corrupted PDF** - Shows graceful fallback to pdfplumber
- **Non-English document** - Shows Textract handles multiple languages

---

## 🤖 Team Member #2: Slack & Business Workflow Automation

### Your Role
Simulate real business workflows by creating Slack webhooks that trigger Box actions and notifications.

### Why This Matters
- Judges want to see **enterprise integration**
- Slack is how teams work - showing it working is impressive
- Demonstrates the system can notify stakeholders automatically
- Shows full workflow: Email → Classification → Slack → Box

---

## 🔔 Task Set #1: Slack Integration & Notifications

### 2.1 Create Slack Webhook for Notifications

**Setup Instructions:**

1. **Create a Slack workspace** (free tier is fine)
   - Go to https://slack.com/create
   - Create a test workspace for demo

2. **Create incoming webhook:**
   - Go to https://api.slack.com/apps
   - Create New App → From scratch
   - Name: "Box Smart Inbox Demo"
   - Select your workspace
   - Go to **Incoming Webhooks** → **Add New Webhook to Workspace**
   - Select a channel (e.g., #documents)
   - Copy the webhook URL

3. **Add to `.env`:**
   ```env
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

### 2.2 Create Slack Notification Triggers

Update backend to send Slack messages when documents are classified:

**File to modify:** `backend/domain_3_box_integration/routes.py`

**Add this notification logic:**
```python
import aiohttp

async def notify_slack(document_type: str, confidence: float, vendor: str):
    """Send classification notification to Slack."""
    
    webhook_url = Config.SLACK_WEBHOOK_URL
    if not webhook_url:
        return
    
    emoji = {
        "invoice": "💰",
        "contract": "📋",
        "receipt": "🧾",
        "resume": "👤",
        "purchase_order": "📦"
    }.get(document_type, "📄")
    
    message = {
        "text": f"{emoji} Document Classified",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{emoji} {document_type.upper()}*\nConfidence: {confidence:.0%}\nVendor: {vendor}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Review in Box"},
                        "url": "https://app.box.com"
                    }
                ]
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        await session.post(webhook_url, json=message)
```

### 2.3 Create "Business Workflow" Slack Actions

**Scenario:** When a high-value invoice is classified, notify finance team immediately

```python
# In approval workflow
if document_type == "invoice" and amount > 10000:
    await notify_slack(
        "HIGH-VALUE INVOICE",
        confidence,
        f"${amount:,.2f} from {vendor}"
    )
```

### 2.4 Track Document Approvals in Slack

Create a Slack thread that shows:
- ✅ Document received
- ✅ Classification complete (with confidence)
- ✅ Approval status
- ✅ Next action (Box task created)

---

## 📊 Task Set #2: Create Fake Business Actions in Box

### 2.5 Simulate Business Processes

**Task 1: Create "Finance Review" Workflow**
- When invoice is classified → create Box task for finance team
- Task assignee: `finance@company.com`
- Task deadline: 48 hours
- Include extracted amount and vendor

**Task 2: Create "Legal Review" Workflow**
- When contract is classified → create Box task for legal team
- Include document preview
- Request signature from legal department

**Task 3: Create "HR Screening" Workflow**
- When resume is classified → create Box task for HR
- Include extracted candidate skills
- Request initial screening

### 2.6 Test Box Folder Organization

```
Box Folder Structure:
├── /Inbox
│   └── [New documents land here]
├── /Invoices
│   └── [Auto-organized by Domain 3]
├── /Contracts
│   └── [Auto-organized by Domain 3]
├── /Resumes
│   └── [Auto-organized by Domain 3]
├── /Needs Review
│   └── [Documents pending approval]
├── /Needs Signature
│   └── [Documents awaiting signature]
└── /Archive
    └── [Completed documents]
```

Verify that documents are automatically organized into the right folders!

---

## 📝 Email Setup Questions - ANSWERED

### ❓ "Do we need our own senders list?"

**Answer: NO** ✅

- **Why:** You're receiving emails, not sending them
- **Current setup:** SendGrid INBOUND webhook catches incoming emails
- **Your email:** Personal Box email is FINE for receiving
- **For sending notifications:** You'll send FROM your business email using SendGrid outbound (optional)

**Recommended setup:**
```
RECEIVING: your-personal-box-email@company.com (receives documents)
NOTIFICATIONS: noreply@company.com (sends updates via Slack instead)
```

### ❓ "Do we need a business email or can I use my Box personal email?"

**Answer: Personal Box email is PERFECT for demo** ✅

**Why this works:**
- Documents come in TO your personal email
- Box routes them automatically
- Extension shows up in YOUR files
- Judges see YOU demo it in real time

**Box Email Setup:**
1. Log into https://www.box.com
2. Look for your email address (usually shown in settings)
3. Use that email as your document inbox
4. SendGrid forwards emails to that address
5. Documents appear in your Box account automatically

**For Production:**
- You'd use `invoices@company.com` or `documents@company.com`
- But for hackathon demo with 1 person, your personal email is ideal

---

## ⚡ Quick Reference: Email Flow

```
┌─────────────────────────────────────────┐
│  Vendor sends PDF to YOUR BOX EMAIL    │
│  (e.g., mason@company.box.com)         │
└────────────┬────────────────────────────┘
             │
             v
┌─────────────────────────────────────────┐
│  SendGrid webhook receives email        │
│  (configured in ngrok URL)              │
└────────────┬────────────────────────────┘
             │
             v
┌─────────────────────────────────────────┐
│  Backend extracts + Textract parses PDF │
│  Cerebras classifies document           │
└────────────┬────────────────────────────┘
             │
             v
┌─────────────────────────────────────────┐
│  Domain 3: Organize in Box              │
│  Create task for reviewer               │
│  Send Slack notification                │
└────────────┬────────────────────────────┘
             │
             v
┌─────────────────────────────────────────┐
│  Judges see live document in Box        │
│  Extension shows classification data    │
│  Slack shows business workflow          │
└─────────────────────────────────────────┘
```

---

## 🎯 Success Criteria for Demo

### Team Member #1 (Docs)
- ✅ Send 5+ emails with different PDF types
- ✅ Verify Textract logs show extraction
- ✅ Show documents appearing in Box
- ✅ Demonstrate classification accuracy

### Team Member #2 (Slack)
- ✅ Slack notifications firing when documents classified
- ✅ Business workflow tasks created in Box
- ✅ Documents auto-organized into correct folders
- ✅ Show judges the full Slack conversation thread

---

## 📅 Timeline

| Time | Activity |
|------|----------|
| **Now** | Team member #1 creates test PDFs |
| **+15 min** | Team member #1 sends emails |
| **+30 min** | Verify documents in Box |
| **+45 min** | Team member #2 sets up Slack |
| **+60 min** | Team member #2 tests workflows |
| **+75 min** | Final verification + recording |
| **+90 min** | Demo ready for judges! 🎉 |

---

## 🚀 Ready to Go?

Your system is production-ready. These tasks just add realistic demo flavor!

**Questions?** Check the main [README.md](README.md) or [DEMO_INSTRUCTIONS.md](DEMO_INSTRUCTIONS.md)

**Record everything** with Playwright:
```bash
npx playwright test playwright-demo.spec.ts --headed --video=on
```

Good luck! 🎬
