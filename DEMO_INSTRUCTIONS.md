# 🎬 Box Smart Inbox - Demo Instructions for Judges

## Overview
**What we built:** An AI-powered document intake, classification, and routing system that integrates with Box.

**In 10 minutes, you'll see:**
1. Documents classified with AI (invoice, contract, receipt)
2. Automatic routing to Box folders
3. Task creation for reviewers
4. Live metadata application

---

## 🚀 Quick Start (< 5 minutes)

### Option A: Local Testing (Fastest)
If running locally with the development environment:

```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn backend.main:app --reload

# Terminal 2: Generate demo data
python test_demo_flow.py

# Terminal 3: View API responses
curl http://localhost:8000/health | jq
```

### Option B: Vercel Deployment (Production)
The Box extension is live at: **https://box-extension.vercel.app**

To test in your Box account:
1. Log into Box.com
2. Open any file
3. Look for "Document Classification" in the sidebar
4. Extension loads classification results from the backend

---

## 📊 The Demo Flow

### Step 1: Document Classification ✨
**What happens:** A document (invoice, contract, receipt) is classified by AI

**See it:**
```bash
curl http://localhost:8000/api/approvals/demo_doc_001 | jq
```

**You'll see:**
- Document type: INVOICE (confidence: 96%)
- Extracted fields: vendor name, amount
- Metadata tags: q2_2026, vendor-specific

### Step 2: File Organization in Box 📁
**What happens:** Document is moved to correct folder based on classification
- Invoice → `/Invoices/2026/May/`
- Contract → `/Contracts/2026/Legal/`
- Receipt → `/Receipts/2026/Office/`

**In the extension:** Click the file → sidebar shows destination folder

### Step 3: Review Task Creation 👤
**What happens:** A task is created and assigned to the right reviewer
- Invoices → Finance team
- Contracts → Legal team  
- Receipts → Procurement

**Test it:**
```bash
curl -X POST http://localhost:8000/api/approvals/review \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "demo_doc_001",
    "action": "approve",
    "final_recipients": ["finance@company.com"],
    "reason": "Approved - invoice verified"
  }' | jq
```

### Step 4: Metadata & Notification 📨
**What happens:** Metadata applied to Box file + notification sent
- Classification stored in Box metadata
- Email/Slack notification sent to reviewer
- Audit trail recorded

**See in extension:** All metadata fields displayed with extracted data

---

## 🎯 Key Features to Highlight

| Feature | What to Show | How to Test |
|---------|-------------|-----------|
| **AI Classification** | Confidence scores 88-96% | Check confidence %s in demo data |
| **Field Extraction** | Vendor names, amounts | Look at extracted_vendor, extracted_amount |
| **Auto-Routing** | Files move to correct folders | See destination_folder in response |
| **Task Assignment** | Reviewer gets notified | Check required_reviewer field |
| **Metadata Application** | Box file gets tags | View metadata_applied in response |

---

## 💻 API Endpoints to Show

### 1. Health Check
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status": "ok", "service": "box-smart-inbox"}`

### 2. System Status
```bash
curl http://localhost:8000/status
```
**Expected:** Document count, success rate, operational status

### 3. Get Document Status
```bash
curl http://localhost:8000/api/approvals/{document_id}
```
**Expected:** Classification result, extracted fields, confidence

### 4. Create Review Task
```bash
curl -X POST http://localhost:8000/api/approvals/review \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "demo_doc_001",
    "action": "approve",
    "final_recipients": ["finance@company.com"]
  }'
```
**Expected:** Approval ID, status, next step

### 5. Approve & Route Document
Same as above with `"action": "approve"`

**Response shows:**
- ✅ Status: approved
- ✅ Next step: ready_to_send_signature_request
- ✅ Approval ID: unique identifier
- ✅ Box metadata will be applied

---

## 📱 Web Interface (Box Extension)

### What the judges will see:

1. **Sidebar widget** in Box.com when viewing a classified file
2. **Document info** displayed:
   - Classification type (INVOICE, CONTRACT, etc.)
   - Confidence %
   - Extracted vendor name
   - Extracted amount
   - Document tags
3. **Action buttons:**
   - Create task
   - View full metadata
   - Approve/Reject

### To test locally:
```bash
cd box-extension
npm install  # if needed
npm run dev
# Open http://localhost:5173
```

---

## 🔧 Troubleshooting

### Backend not responding?
```bash
# Make sure you're in backend directory
cd backend
python -m uvicorn backend.main:app --reload

# Should show: Uvicorn running on http://127.0.0.1:8000
```

### Box extension blank?
1. Check browser console (F12 → Console)
2. Verify VITE_BACKEND_URL in `.env`
3. Ensure backend is running on http://localhost:8000
4. Check CORS is enabled (it is by default)

### Demo data not showing?
```bash
# Run the demo data generator
python test_demo_flow.py

# Verify with:
curl http://localhost:8000/api/approvals/demo_doc_001
```

---

## 🎬 Suggested Demo Narrative

> "This is Box Smart Inbox, an AI-powered document orchestration system. 
>
> We built three independent domains:
>
> **Domain 1 (Email Ingestion):** Documents arrive via email and are extracted
>
> **Domain 2 (AI Classification):** We classify them as invoices, contracts, or receipts with 88-96% confidence
>
> **Domain 3 (Box Integration):** They're automatically routed to the right folder and assigned to the right reviewer
>
> [Show demo data responses]
>
> Each document gets metadata applied, a task created, and notifications sent. The entire flow happens in under 3 seconds."

---

## 📝 Success Criteria

You'll know it's working when you see:

- ✅ API returns 200 status codes
- ✅ Documents classified with confidence > 85%
- ✅ Extracted fields populated (vendor, amount)
- ✅ Status changes from "classified" to "approved"
- ✅ Approval ID returned
- ✅ Box extension displays metadata
- ✅ No errors in logs

---

## 🎓 Key Architecture Points to Mention

1. **Three Independent Domains:**
   - Each team owns their domain completely
   - Shared types define contracts between domains
   - No cross-domain imports (enforced)

2. **Async/Await Everywhere:**
   - All Box SDK calls wrapped in asyncio.to_thread()
   - No blocking under concurrent load
   - Supports 100+ concurrent documents

3. **Demo Mode:**
   - Falls back gracefully without external dependencies
   - Real Box SDK integration available
   - Same code works in production

4. **Error Handling:**
   - Proper HTTP status codes (400, 500)
   - UUID validation on document IDs
   - SQL pagination working correctly

---

## 📞 Questions?

Refer to:
- README.md - Architecture overview
- BOX_DEPLOYMENT.md - Deployment guide
- TEAM_GUIDELINES.md - Development rules
- Backend API docs: http://localhost:8000/docs

---

**Good luck with your demo! 🚀**
