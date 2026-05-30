# 🎬 Arcade Demo Script - Box Smart Inbox

## 🏗️ Full Tech Stack (for slides/intro)

### Cloud & Deployment
| Service | Purpose |
|---------|---------|
| **Render** | Backend hosting (Python FastAPI) |
| **Vercel** | Box extension hosting (React) |
| **Render PostgreSQL** | Document state tracking |

### AI & Document Processing
| Service | Purpose |
|---------|---------|
| **Cerebras** (gpt-oss-120b) | AI classification engine |
| **AWS Textract** | PDF text extraction (OCR) |
| **pdfplumber / PyPDF2** | Local PDF fallback |
| **Groq / Gemini** | LLM fallback providers |

### Box Platform
| Service | Purpose |
|---------|---------|
| **Box SDK Gen** | File management, metadata, tasks |
| **Box V2 Webhooks** | FILE.UPLOADED triggers |
| **Box Email Upload** | Inbox.wd6jkg7cbj1k47n2@u.box.com |
| **Box UI Elements** | Extension sidebar |

### Notifications & Communication
| Service | Purpose |
|---------|---------|
| **Slack Incoming Webhooks** | Real-time team notifications |
| **SendGrid** | Email ingestion + outbound alerts |

### Backend Framework
| Tool | Version | Purpose |
|------|---------|---------|
| FastAPI | 0.109.0 | REST API |
| Python | 3.11.8 | Runtime |
| AsyncPG | 0.31.0 | Async PostgreSQL |
| httpx | 0.25.2 | Async HTTP client |
| Pydantic | 2.6.1 | Data validation |

### Frontend Framework
| Tool | Version | Purpose |
|------|---------|---------|
| React | 18.2.0 | Extension UI |
| TypeScript | 5.0.0 | Type safety |
| Vite | 4.0.0 | Build tool |
| Axios | 1.6.0 | API calls |

### Testing
| Tool | Purpose |
|------|---------|
| **Playwright** | End-to-end browser automation |
| pytest | Unit tests |
| pytest-asyncio | Async test support |

---

## 🎬 Arcade Recording Script

### SCENE 1: Architecture Overview (30 seconds)
> *Show a slide or diagram of the system*

**Narration:**
"Box Smart Inbox is an AI-powered document automation system built on three independent domains.
Documents arrive by email, get classified by Cerebras AI, and automatically sort into Box.
Zero manual filing. Zero human intervention. Let's see it live."

---

### SCENE 2: The Inbox (15 seconds)
> *Open Box → Project-Smart-Sort → Inbox folder*

**Steps:**
1. Navigate to `app.box.com`
2. Open **Project-Smart-Sort** folder
3. Click **Inbox** folder
4. Show: "Here's our smart inbox — think of it as a filing tray that sorts itself"

**What to show:**
- The Inbox folder with files waiting
- The other folders: Invoices, Contracts, Receipts, Resumes, Purchase Orders

---

### SCENE 3: Send a Test Email (20 seconds)
> *Open email client, compose email*

**Steps:**
1. Open Gmail / email client
2. Compose new email:
   - **To:** `Inbox.wd6jkg7cbj1k47n2@u.box.com`
   - **Subject:** `Invoice from ACME Corporation - May 2026`
   - **Body:** `Please process this invoice for approval`
   - **Attach:** `invoice_acme.pdf`
3. Send it
4. Say: "I just emailed an invoice to our Box inbox address"

---

### SCENE 4: Trigger the AI Pipeline (20 seconds)
> *Open PowerShell / terminal - run process-inbox*

**Steps:**
1. Open PowerShell
2. Run:
```powershell
Invoke-WebRequest `
  -Uri "https://project-smart-sort.onrender.com/api/process-inbox" `
  -Method POST -UseBasicParsing | Select-Object -ExpandProperty Content
```
3. Show the JSON response:
```json
{
  "status": "complete",
  "total": 5,
  "sorted": 5,
  "results": [
    {
      "file": "invoice_acme.pdf",
      "status": "sorted",
      "doc_type": "invoice",
      "confidence": "96%",
      "destination": "/Invoices/2026/May",
      "assigned_to": "finance@company.com"
    }
  ]
}
```

**Narration:** "Watch — our Cerebras AI reads the document, classifies it as an invoice with 96% confidence, and routes it automatically."

---

### SCENE 5: Watch Box Sort the Documents (30 seconds)
> *Switch back to Box - refresh and show*

**Steps:**
1. Switch to Box browser tab
2. Refresh the Project-Smart-Sort folder
3. Show: Inbox now empty (or reduced)
4. Click **Invoices** folder
5. Navigate to **Invoices → 2026 → May**
6. Show the invoice file is now there
7. Say: "The file moved automatically from Inbox to Invoices/2026/May"

---

### SCENE 6: The Box Extension (40 seconds)
> *Click on the sorted file to open it*

**Steps:**
1. Click on the invoice file
2. Box opens the file preview
3. Look at the **right sidebar** — extension loads
4. Show the extension displaying:
   - **Document Type:** INVOICE
   - **Confidence:** 96%
   - **Vendor:** ACME Corporation
   - **Amount:** $25,000.00
   - **Assigned to:** Finance Team
5. Say: "Our Box extension sidebar shows exactly what the AI found inside the document"
6. Click **"Create Review Task"** button in the extension
7. Show task appears in Box

---

### SCENE 7: Slack Notification (20 seconds)
> *Switch to Slack*

**Steps:**
1. Open Slack → **Box Smart Inbox** workspace → **#documents** channel
2. Show the notification:
   ```
   📄 New Invoice for Review
   Document ID: abc-123
   Assigned to: finance@company.com
   Confidence: 96%
   Vendor: ACME Corporation
   Amount: $25,000.00
   📂 Review in Box
   ```
3. Click the **📂 Review in Box** link
4. Show it opens directly to the file in Box
5. Say: "The finance team gets notified instantly in Slack with a direct link"

---

### SCENE 8: Different Document Types (30 seconds)
> *Show multiple document types being sorted*

**Steps:**
1. Go back to Box Inbox (if any files remain)
2. Show files sorted into different folders:
   - Contract → `/Contracts/2026/May`
   - Receipt → `/Receipts`
   - Resume → `/Resumes`
3. Open one of each and show the extension sidebar
4. Say: "Every document type routes to the right place automatically"

---

### SCENE 9: Backend Health + API (20 seconds)
> *Show the live API*

**Steps:**
1. Open browser
2. Navigate to `https://project-smart-sort.onrender.com/health`
3. Show: `{"status": "ok", "service": "box-smart-inbox"}`
4. Navigate to `https://project-smart-sort.onrender.com/docs`
5. Show the Swagger UI with all endpoints
6. Say: "Full REST API, all 3 domains, production-deployed on Render"

---

### SCENE 10: Playwright Test (optional - 30 seconds)
> *Run automated test in terminal*

**Steps:**
1. Open terminal
2. Run:
```bash
npx playwright test playwright-demo.spec.ts -g "Quick API Test" --headed
```
3. Show tests passing
4. Say: "Fully automated tests verify the entire pipeline end-to-end"

---

## 📊 Key Stats for Narration

| Metric | Value |
|--------|-------|
| **Classification accuracy** | 96% confidence (invoice), 92% (contract), 88% (receipt) |
| **Processing time** | ~3 seconds email → sorted |
| **API endpoints** | 15+ REST endpoints |
| **Document types** | 7 (Invoice, Contract, Resume, Receipt, ID, PO, Other) |
| **Domains** | 3 independent services |
| **LLM provider** | Cerebras gpt-oss-120b |
| **PDF extraction** | AWS Textract + pdfplumber fallback |
| **Deployment** | Render (backend) + Vercel (extension) |

---

## 🎯 One-Sentence Pitches

**Technical:** "Three-domain FastAPI microservices using Cerebras AI and AWS Textract to automatically classify and route documents in Box, with real-time Slack notifications."

**Business:** "An AI-powered smart inbox for Box that reads, understands, and files every document automatically — replacing manual sorting entirely."

**Simple:** "Email a PDF, it appears in the right Box folder in 3 seconds. The AI does the work."

---

## 🔗 Live URLs for Demo

| What | URL |
|------|-----|
| **Backend API** | https://project-smart-sort.onrender.com/health |
| **API Docs** | https://project-smart-sort.onrender.com/docs |
| **Box Extension** | https://box-extension.vercel.app |
| **Box Inbox** | app.box.com → Project-Smart-Sort → Inbox |
| **Process Inbox** | POST https://project-smart-sort.onrender.com/api/process-inbox |
| **Box Inbox Email** | Inbox.wd6jkg7cbj1k47n2@u.box.com |

---

## ⚠️ Pre-Recording Checklist

- [ ] Backend health: `curl https://project-smart-sort.onrender.com/health`
- [ ] Box logged in at app.box.com
- [ ] Slack open on #documents channel
- [ ] Test PDF files ready to email
- [ ] Terminal/PowerShell open with process-inbox command ready
- [ ] Browser tabs pre-opened: Box, Slack, Render logs
- [ ] Inbox has 3-5 files already waiting (or send emails first)
- [ ] Extension visible in Box sidebar (open a file to verify)

---

## 🎬 Ideal Arcade Recording Order

```
1. [SLIDE] Tech stack overview (30s)
2. [BOX] Show folder structure (15s)
3. [EMAIL] Send test email (20s)
4. [TERMINAL] Run process-inbox (20s)
5. [BOX] Show files sorted (30s)
6. [BOX] Open file → extension sidebar (40s)
7. [SLACK] Show notification + click link (20s)
8. [BROWSER] Show live API (20s)
9. [TERMINAL] Playwright test (30s, optional)
Total: ~3.5 minutes
```
