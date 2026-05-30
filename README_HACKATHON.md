# 🚀 Box Smart Inbox - Hackathon Edition

**Event:** CascadiaJS AI Hackathon 2 (Tonight!)  
**Repository:** Clean skeleton, ready for team work  
**Status:** ✅ All setup complete, waiting for credentials

---

## Quick Start (Pick Your Role!)

**Are you:**

### 👤 Mason (Manager/Owner)
1. Read: [`MANAGER_TASKS.md`](./MANAGER_TASKS.md)
2. Get API keys (SendGrid, Box, Cerebras)
3. Create `.env` file
4. Share with team
5. Coordinate team during hackathon

### 👤 Person A (Domain 1 - Email)
1. Clone repo: `git clone https://github.com/sabinMas/hackathon-skeleton.git`
2. Read: [`GETTING_STARTED.md`](./GETTING_STARTED.md)
3. Read: [`DOMAIN_1_SETUP.md`](./DOMAIN_1_SETUP.md)
4. Wait for Mason to provide `.env` file
5. Implement email ingestion (`backend/domain_1_email/service.py`)

### 👤 Person B (Domain 2 - AI)
1. Clone repo: `git clone https://github.com/sabinMas/hackathon-skeleton.git`
2. Read: [`GETTING_STARTED.md`](./GETTING_STARTED.md)
3. Read: [`DOMAIN_2_SETUP.md`](./DOMAIN_2_SETUP.md)
4. Wait for Mason to provide `.env` file
5. Implement LLM classification (`backend/domain_2_classifier/service.py`)

### 👤 Person C (Domain 3 - Box)
1. Clone repo: `git clone https://github.com/sabinMas/hackathon-skeleton.git`
2. Read: [`GETTING_STARTED.md`](./GETTING_STARTED.md)
3. Read: [`DOMAIN_3_SETUP.md`](./DOMAIN_3_SETUP.md)
4. Wait for Mason to provide `.env` file
5. Implement Box integration (`backend/domain_3_box_integration/service.py`)

---

## What's Pre-Written (Safe!)

✅ **Safe to use - pre-hackathon skeleton:**
- Project structure and folders
- Type contracts (`backend/shared/types.py`)
- Route endpoints (defined but NOT implemented)
- Test utilities and fixtures
- Documentation and guides
- Box UI Extension (React skeleton)
- Demo materials and scripts

❌ **You MUST implement - nothing here:**
- Domain 1: Email ingestion logic
- Domain 2: LLM classification logic
- Domain 3: Box integration logic

**All domain services have `raise NotImplementedError("TODO: Implement...")` with clear instructions. This skeleton is 100% safe for any hackathon rules.**

---

## Repository Structure

```
hackathon-skeleton/
├── GETTING_STARTED.md              ← Everyone reads this first
├── MANAGER_TASKS.md                ← Mason's guide
├── DOMAIN_1_SETUP.md               ← Person A's guide
├── DOMAIN_2_SETUP.md               ← Person B's guide
├── DOMAIN_3_SETUP.md               ← Person C's guide
├── DEMO_SCRIPT.md                  ← What to say to judges
├── DEMO_CHECKLIST.md               ← How to run the demo
├── .env.setup.md                   ← API key setup guide
├── HACKATHON_PREP_SUMMARY.md       ← High-level overview
│
├── backend/
│   ├── main.py                     ← FastAPI app (orchestration)
│   ├── domain_1_email/             ← TODO: Implement email webhook
│   ├── domain_2_classifier/        ← TODO: Implement LLM classification
│   ├── domain_3_box_integration/   ← TODO: Implement Box routing
│   └── shared/                     ← Types, config, utilities
│
├── box-extension/                  ← React UI (ready to build)
│   ├── manifest.json
│   ├── package.json
│   ├── public/
│   └── src/
│
├── test_documents/                 ← Sample PDFs (convert .txt to PDF)
│   ├── sample_invoice.txt
│   ├── sample_contract.txt
│   └── ... (more samples)
│
├── docs/
│   ├── SYSTEM_FLOW.md              ← Architecture with diagrams
│   ├── ARCHITECTURE.md             ← System design
│   ├── API_REFERENCE.md            ← API endpoints
│   └── CRISIS_RUNBOOK.md           ← Troubleshooting
│
└── requirements.txt                ← Python dependencies
```

---

## Team Setup Checklist

**Before Event (Manager):**
- [ ] Get 8 API keys (SendGrid, Box, Cerebras)
- [ ] Create `.env` file
- [ ] Set up ngrok tunnel
- [ ] Share `.env` with team securely
- [ ] Create Discord/Slack channel

**During Event (Everyone):**
- [ ] Clone repo
- [ ] Read your role's setup file
- [ ] Set up Python environment: `python -m venv venv && pip install -r requirements.txt`
- [ ] Verify setup: `pytest -v` (tests will fail on business logic - that's OK!)
- [ ] Start backend: `uvicorn backend.main:app --reload`
- [ ] Watch 1-hour educational demo
- [ ] Start coding!

---

## Type Contracts (THE BOUNDARIES)

These define how domains communicate. **Never modify after T+2h:**

```python
# Domain 1 Output → Domain 2 Input
IngestedDocument(
    id: str                    # UUID
    filename: str              # "invoice.pdf"
    content: str               # FULL TEXT (email + attachments)
    content_type: str          # "application/pdf"
    source: str                # "email"
    email_from: str            # "bob@acme.com"
)

# Domain 2 Output → Domain 3 Input
ClassificationResult(
    document_id: str           # UUID
    doc_type: str              # "invoice" (or contract, resume, etc.)
    confidence: float          # 0.0 to 1.0
    extracted_fields: dict     # {"vendor": "Acme", "amount": 5000}
    required_reviewer: str     # "finance", "legal", etc.
    metadata_tags: list        # ["vendor:acme", "q2_2024"]
)

# Domain 3 Output → API Response
ProcessingResult(
    document_id: str           # UUID
    box_file_id: str           # Box file ID
    destination_folder: str    # "/Invoices/2024/May/"
    status: str                # "success" or "failure"
    task_id: str               # Box task ID
    assigned_to: str           # "reviewer@company.com"
    notification_sent_to: list # ["slack", "email"]
)
```

---

## Success Criteria

**Your domain is DONE when:**
- [ ] All your tests pass: `pytest backend/domain_X/tests/ -v`
- [ ] No `NotImplementedError` in your code
- [ ] Your domain implements all TODO items
- [ ] You can explain it to someone else

**Hackathon is successful when:**
- [ ] End-to-end flow works (email → classify → Box)
- [ ] All tests passing: `pytest -v`
- [ ] Demo runs smoothly
- [ ] Judges are impressed!

---

## Git Workflow

**Each person should:**
```bash
# Create your domain branch
git checkout -b feature/domain-X-implementation

# Make changes ONLY in your domain folder
git add backend/domain_X_*/

# Commit with clear messages
git commit -m "[domain-X] Implement specific feature"

# Push to your branch
git push origin feature/domain-X-implementation

# When done: Create PR
# Manager will review and merge when tests pass
```

---

## Timeline

| Time | What's Happening | Your Role |
|------|------------------|-----------|
| T-1h | Event doors open | Manager: Provide `.env` file |
| T+0 | Event starts | Everyone: Clone repo, verify setup |
| T+1h | AI/Box demo talk | Everyone: Listen and learn |
| T+2h | **CODING BEGINS** | Start implementing your domain! |
| T+8h | Mid-point check | Manager: Check progress |
| T+12h | Integration | Merge PRs, run full tests |
| T+16h | Integration testing | Test end-to-end flow |
| T+18h | Demo prep | Prepare demo materials |
| T+22h | Final review | Everything working? |
| T+24h | **DEMO TIME!** | Show judges what you built! |

---

## Need Help?

**Quick questions?**
1. Read your role's setup file (has troubleshooting section)
2. Check `CRISIS_RUNBOOK.md` (common issues)
3. Ask the team on Discord/Slack

**Confused about architecture?**
1. Read `docs/SYSTEM_FLOW.md` (visual diagrams)
2. Read `docs/ARCHITECTURE.md` (detailed design)
3. Ask Manager or team

**Can't get tests to pass?**
1. Make sure you implemented all TODOs
2. Check test fixtures in `backend/shared/fixtures.py`
3. Ask Manager for help

---

## Important Reminders

✅ **DO:**
- Read your role's setup file completely
- Implement ALL TODO comments in your domain
- Test your domain in isolation first
- Ask for help early if stuck
- Commit regularly with clear messages
- Run tests before asking for merge

❌ **DON'T:**
- Import from other domains (breaks independence)
- Modify `backend/shared/types.py` after T+2h
- Skip reading your setup file
- Leave NotImplementedError in your code
- Try to do everything at once

---

## Files That Matter

**Read These (In Order):**
1. This file (you're reading it! ✓)
2. Your role-specific setup file
3. `TEAM_GUIDELINES.md` (team rules)
4. `docs/SYSTEM_FLOW.md` (architecture)

**Reference During Coding:**
- Your domain's TODOs in service.py
- `backend/shared/fixtures.py` (test data)
- Your domain's test file (see what tests expect)
- `AGENT_DOMAIN_X.md` (detailed domain guide)

**Before Demo:**
- `DEMO_SCRIPT.md` (exact words to say)
- `DEMO_CHECKLIST.md` (minute-by-minute)
- `SYSTEM_FLOW.md` (show judges the architecture)

---

## You've Got Everything!

✅ Clean skeleton with no surprises  
✅ Clear role assignments  
✅ Step-by-step guides for each domain  
✅ Type contracts that prevent conflicts  
✅ Complete demo materials  
✅ Troubleshooting guides  
✅ UI Extension ready to build  
✅ Test samples and fixtures  

**All you need is:**
1. API credentials from Manager
2. 24 hours of focused work
3. Great teamwork
4. Confidence in what you built

---

## Let's Ship It! 🚀

**The codebase is ready. The guides are written. The architecture is sound. All you need to do is implement the domain logic, pass the tests, and demo to the judges.**

**Go build something amazing!** 💪

---

**Questions? Start here:**
- Manager: See `MANAGER_TASKS.md`
- Person A: See `DOMAIN_1_SETUP.md`
- Person B: See `DOMAIN_2_SETUP.md`
- Person C: See `DOMAIN_3_SETUP.md`

**Good luck! The event starts tonight! 🎉**
