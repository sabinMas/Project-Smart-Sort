# Getting Started - Box Smart Inbox Hackathon

**Welcome to the team!** This guide walks you through setup and your role.

---

## 🚀 Quick Setup (Everyone - 15 minutes)

### Step 1: Clone the Repo
```bash
git clone https://github.com/sabinMas/hackathon-skeleton.git
cd hackathon-skeleton
```

### Step 2: Create Python Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Wait for Manager
⏸️ **STOP HERE** - Manager (Mason) will provide `.env` file with API keys

### Step 4: Verify Everything Works
```bash
# Run tests (they might fail on business logic, that's OK!)
pytest -v

# Start server (in separate terminal)
uvicorn backend.main:app --reload

# Check API docs
open http://localhost:8000/docs
```

---

## 👥 Find Your Role

**Are you:**

### 👤 Person A - Domain 1 (Email Ingestion)?
→ Read: [`DOMAIN_1_SETUP.md`](./DOMAIN_1_SETUP.md)

### 👤 Person B - Domain 2 (AI Classification)?
→ Read: [`DOMAIN_2_SETUP.md`](./DOMAIN_2_SETUP.md)

### 👤 Person C - Domain 3 (Box Integration)?
→ Read: [`DOMAIN_3_SETUP.md`](./DOMAIN_3_SETUP.md)

### 👤 Manager (Mason)?
→ Read: [`MANAGER_TASKS.md`](./MANAGER_TASKS.md)

---

## 📋 What's Pre-Written (Safe to Use)

✅ **You CAN use:**
- Project structure and folder organization
- Type contracts (`backend/shared/types.py`) - data models that connect domains
- Route endpoints (defined but empty)
- Test utilities and fixtures
- Documentation and guides
- Box UI Extension (React skeleton)

❌ **You MUST implement:**
- Domain 1: Email ingestion logic (parsing, extraction)
- Domain 2: LLM classification logic (calling API, parsing response)
- Domain 3: Box integration logic (uploading, metadata, tasks)

---

## 🎯 Success Criteria

Your domain is done when:

### Domain 1 ✅
- [ ] `EmailIngestionService.ingest_email()` implemented
- [ ] `handle_email_webhook()` route working
- [ ] SendGrid webhook signature validated
- [ ] Email attachments extracted
- [ ] Returns `IngestedDocument` object
- [ ] All Domain 1 tests pass: `pytest backend/domain_1_email/tests/ -v`

### Domain 2 ✅
- [ ] `ClassificationService.classify()` implemented
- [ ] Calls LLM (Cerebras/Groq/Gemini)
- [ ] Parses JSON response
- [ ] Validates confidence 0.0-1.0
- [ ] Maps doc_type to required_reviewer
- [ ] Returns `ClassificationResult` object
- [ ] All Domain 2 tests pass: `pytest backend/domain_2_classifier/tests/ -v`

### Domain 3 ✅
- [ ] `BoxIntegrationService.process()` implemented
- [ ] Routes file to correct Box folder
- [ ] Applies metadata tags
- [ ] Creates review task
- [ ] Sends Slack/Email notifications
- [ ] Returns `ProcessingResult` object
- [ ] All Domain 3 tests pass: `pytest backend/domain_3_box_integration/tests/ -v`

---

## 🔑 Type Contracts (THE RULES)

These define how domains communicate. **DO NOT MODIFY after T+2h:**

**IngestedDocument** (Domain 1 → Domain 2)
```python
id: str                    # UUID
filename: str              # Original filename
content: str               # Full extracted text
content_type: str          # MIME type
source: str                # "email" or "box_file_request"
email_from: str | None     # Sender email
```

**ClassificationResult** (Domain 2 → Domain 3)
```python
document_id: str           # Reference to IngestedDocument.id
doc_type: str              # invoice|contract|resume|receipt|id_document|purchase_order|other
confidence: float          # 0.0 to 1.0
extracted_fields: dict     # Vendor, amount, date, etc.
required_reviewer: str     # finance|legal|hr|procurement|None
metadata_tags: list        # ["vendor:acme", "q2_2024"]
```

**ProcessingResult** (Domain 3 → API)
```python
document_id: str           # Reference to IngestedDocument.id
box_file_id: str           # File ID in Box
destination_folder: str    # /Invoices/2024/May/
status: str                # success|failure|escalated
task_id: str | None        # Box task ID
assigned_to: str | None    # Reviewer email
notification_sent_to: list # ["slack", "email"]
```

---

## 📚 Key Documentation

**Before you start coding:**
- [ ] Read your domain's SETUP file
- [ ] Read `TEAM_GUIDELINES.md` (team rules)
- [ ] Read `docs/ARCHITECTURE.md` (system design)
- [ ] Read `docs/SYSTEM_FLOW.md` (complete data flow)

**While you're coding:**
- [ ] Reference `AGENT_DOMAIN_X.md` (detailed domain guide)
- [ ] Check `CRISIS_RUNBOOK.md` if you hit issues
- [ ] Use `backend/shared/fixtures.py` for test data

**For the demo:**
- [ ] Read `DEMO_SCRIPT.md` (what we're showing judges)
- [ ] Understand `DEMO_CHECKLIST.md` (how we'll run it)

---

## 🚨 Common Mistakes (Avoid!)

❌ **Don't:**
- Import from other domains (breaks independence)
- Modify `backend/shared/types.py` after T+2h
- Modify another domain's files
- Skip writing tests for your domain
- Leave NotImplementedError in your code

✅ **Do:**
- Test your domain in isolation
- Use shared fixtures and utilities
- Commit to your domain's branch
- Talk to the team if you're blocked
- Make your tests pass!

---

## 🔄 Git Workflow

**Each person should:**
```bash
# Create your domain branch
git checkout -b feature/domain-X-implementation

# Make changes only in your domain folder
git add backend/domain_X_*/

# Commit with clear messages
git commit -m "[domain-X] Implement specific feature"

# Push to your branch
git push origin feature/domain-X-implementation

# Create PR when ready
# Manager will merge when all tests pass
```

---

## ❓ Need Help?

**Blocked?**
1. Check your domain's SETUP file
2. Read `CRISIS_RUNBOOK.md` 
3. Look at test fixtures in `backend/shared/fixtures.py`
4. Ask the team in Discord/Slack
5. Ask Manager (Mason) for guidance

**Have questions about your role?**
1. Read your domain's SETUP file
2. Check `TEAM_GUIDELINES.md`
3. Ask the team

**Confused about the architecture?**
1. Read `docs/ARCHITECTURE.md`
2. Read `docs/SYSTEM_FLOW.md`
3. Draw it out on whiteboard
4. Ask the team

---

## 🎯 Timeline

| Time | Milestone | Your Task |
|------|-----------|-----------|
| T+0 | Event starts | Clone repo, verify setup |
| T+1h | Demo | Watch and learn |
| T+2h | Coding begins | Start implementing |
| T+8h | Mid-point | Domain complete & tested |
| T+16h | Integration | All domains working together |
| T+20h | Demo ready | Full end-to-end working |
| T+22h | Final prep | Polish & troubleshoot |
| T+24h | **DEMO TIME** | Show judges what you built! |

---

## ✨ You've Got This!

You have a clean skeleton, clear domains, and everything you need. Go build something amazing! 🚀

**Questions before you start?** Ask the team!

---

**Built for CascadiaJS AI Hackathon 2**
