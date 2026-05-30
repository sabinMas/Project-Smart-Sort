# 🎬 3-Minute Arcade Demo Script - Box Smart Inbox

## ⏱️ Scene Breakdown (exactly 3:00)

| Scene | Duration | Cumulative |
|-------|----------|-----------|
| 1. Hook + Problem | 0:20 | 0:20 |
| 2. Show Box Inbox | 0:20 | 0:40 |
| 3. Send Email | 0:20 | 1:00 |
| 4. AI Pipeline Running | 0:25 | 1:25 |
| 5. Files Sorted in Box | 0:25 | 1:50 |
| 6. Extension Sidebar | 0:35 | 2:25 |
| 7. Slack Notification | 0:20 | 2:45 |
| 8. Tech Stack Close | 0:15 | 3:00 |

---

## 🎙️ SCENE 1 — Hook (0:00 – 0:20)
**Screen:** Show a cluttered email inbox full of PDFs

> *"Every business drowns in documents — invoices, contracts, resumes — all arriving by email, all filed manually. Box Smart Inbox changes that. Watch what happens when you email a document to our system."*

---

## 📂 SCENE 2 — Box Inbox (0:20 – 0:40)
**Screen:** Open `app.box.com` → Project-Smart-Sort folder

> *"This is our Box workspace. The Inbox is our drop zone. The sorted folders — Invoices, Contracts, Resumes, Receipts — are where documents automatically land after our AI reads them."*

**Click through:** Show Inbox → Invoices → Contracts → back to Inbox

---

## 📧 SCENE 3 — Send Email (0:40 – 1:00)
**Screen:** Open email, compose, send

**Compose:**
```
TO:      Inbox.wd6jkg7cbj1k47n2@u.box.com
SUBJECT: Invoice from ACME Corporation
ATTACH:  invoice_acme.pdf
```

> *"I'm emailing an invoice PDF directly to our Box inbox address. No login. No portal. Just email."*

**Hit send. Switch immediately to Box — file appears in Inbox.**

---

## ⚡ SCENE 4 — AI Pipeline (1:00 – 1:25)
**Screen:** Split or switch to terminal

```powershell
Invoke-WebRequest `
  -Uri "https://project-smart-sort.onrender.com/api/process-inbox" `
  -Method POST -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Show response:**
```json
{
  "status": "complete",
  "sorted": 1,
  "results": [{
    "file": "invoice_acme.pdf",
    "doc_type": "invoice",
    "confidence": "96%",
    "destination": "/Invoices/2026/May"
  }]
}
```

> *"Our backend — running on Render — downloads the file, sends it through AWS Textract for OCR, then Cerebras AI classifies it as an invoice with 96% confidence."*

---

## 📁 SCENE 5 — Files Sorted (1:25 – 1:50)
**Screen:** Switch to Box, refresh

1. Refresh Project-Smart-Sort folder
2. Click **Invoices**
3. Click **2026 → May**
4. Invoice file is there ✅

> *"The file is gone from the Inbox and now lives in Invoices/2026/May — automatically. No human touched it."*

---

## 🔍 SCENE 6 — Extension Sidebar (1:50 – 2:25)
**Screen:** Click the invoice file in Box

> *"Now watch the sidebar."*

**Extension loads and shows:**
```
┌─────────────────────────────┐
│  Document Classification    │
│                             │
│  📄 INVOICE                 │
│  Confidence: 96%            │
│                             │
│  Vendor:  ACME Corporation  │
│  Amount:  $25,000.00        │
│  Assigned: Finance Team     │
│                             │
│  [Create Review Task]       │
└─────────────────────────────┘
```

> *"Our Box extension reads the AI's output — document type, confidence score, extracted vendor name, dollar amount, assigned reviewer. All pulled from inside the PDF automatically."*

**Click "Create Review Task"** → show task appears

> *"One click creates a Box task assigned to the finance team."*

---

## 💬 SCENE 7 — Slack (2:25 – 2:45)
**Screen:** Switch to Slack → #documents channel

**Show message:**
```
📄 New Invoice for Review
Assigned to: finance@company.com
Confidence: 96%
Vendor: ACME Corporation
Amount: $25,000.00
📂 Review in Box
```

**Click the link** → Box opens directly to the file

> *"The finance team gets notified in Slack instantly with a direct link to the file. Everything connected, fully automated."*

---

## 🏗️ SCENE 8 — Tech Stack Close (2:45 – 3:00)
**Screen:** Show `https://project-smart-sort.onrender.com/docs` (Swagger UI)

> *"Built on FastAPI, Cerebras AI, AWS Textract, Box SDK, Slack — deployed on Render and Vercel. Three independent domains. One seamless pipeline. Box Smart Inbox."*

**Fade out.**

---

## 🎙️ Full Narration Script (Word for Word)

```
[0:00] Every business drowns in documents — invoices, contracts,
       resumes — all arriving by email, all filed manually.
       Box Smart Inbox changes that.

[0:20] This is our Box workspace. The Inbox is our drop zone.
       Invoices, Contracts, Resumes — where documents automatically
       land after our AI reads them.

[0:40] I'm emailing an invoice PDF directly to our Box inbox address.
       No login. No portal. Just email.

[1:00] Our backend downloads the file, runs it through AWS Textract
       for OCR, then Cerebras AI classifies it as an invoice
       with 96% confidence.

[1:25] The file is gone from Inbox and lives in Invoices/2026/May —
       automatically. No human touched it.

[1:50] Now watch the sidebar. Our Box extension shows document type,
       confidence score, extracted vendor name, dollar amount,
       and assigned reviewer — all from inside the PDF.

[2:15] One click creates a Box review task assigned to finance.

[2:25] The finance team gets notified in Slack instantly with
       a direct link. Everything connected. Fully automated.

[2:45] Built on FastAPI, Cerebras AI, AWS Textract, Box SDK,
       and Slack — three independent domains, one seamless pipeline.
       Box Smart Inbox.
```

---

## ✅ Pre-Recording Setup (Do This First)

```powershell
# 1. Confirm backend is live
(Invoke-WebRequest "https://project-smart-sort.onrender.com/health" -UseBasicParsing).Content

# 2. Send 2-3 test emails BEFORE recording
#    TO: Inbox.wd6jkg7cbj1k47n2@u.box.com
#    So files are waiting in Inbox when camera rolls

# 3. Open these tabs before recording:
#    Tab 1: app.box.com/folder/385610054142 (Project-Smart-Sort)
#    Tab 2: Slack #documents channel
#    Tab 3: https://project-smart-sort.onrender.com/docs
#    Tab 4: PowerShell terminal
```

## 🎬 Arcade Tips
- Record at **1280x800** for clean capture
- Use **Arcade's zoom** feature on the extension sidebar (Scene 6)
- **Pause/cut** between Scene 4 (terminal) and Scene 5 (Box) if needed
- Highlight the confidence score and extracted fields in Scene 6 — that's the money shot
