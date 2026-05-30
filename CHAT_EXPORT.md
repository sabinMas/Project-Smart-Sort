# Hackathon Project Planning Chat Export

**Date:** May 29, 2026  
**Project:** Box Smart Inbox - CascadiaJS AI Hackathon 2  
**Team Lead:** Mason (masonsabin@gmail.com)  
**Status:** Ready for Launch (11 PM Tonight)

---

## Executive Summary

This document captures the complete planning, architecture decisions, and team setup for the Box Smart Inbox hackathon project. It documents how a team leveraged agentic coding patterns, rigorous pre-work planning, and clear role assignments to build a production-quality system in 24 hours.

**Key Achievements:**
- ✅ Complete backend skeleton with 3 independent domains
- ✅ Type contracts preventing hallucination cascades
- ✅ Role-specific setup guides for each team member
- ✅ Professional project management structure
- ✅ Agentic coding best practices built in
- ✅ Demo materials and scripts ready
- ✅ Risk mitigation strategies documented

---

## Project Overview

### What We're Building

**Box Smart Inbox** - An AI-powered document intake, classification, and routing system that integrates with Box.

**The Problem:** Companies receive hundreds of documents via email (invoices, contracts, receipts, resumes) that need to be classified, routed to the right person, and reviewed.

**The Solution:** Automatically classify documents with AI, apply metadata, create tasks, and notify the right team—all within Box's native interface.

### Architecture: Three Independent Domains

```
Email/Upload
    ↓
[Domain 1: Email Ingestion] → IngestedDocument
    ↓
[Domain 2: AI Classification] → ClassificationResult
    ↓
[Domain 3: Box Integration] → ProcessingResult
    ↓
[Notifications] → Slack, Email, Dashboard
```

**Domain Independence:** Each domain is completely isolated. Teams can work in parallel without conflicts. Communication happens only through type contracts (locked data structures).

---

## Team Structure

### Roles Assigned

**Mason (Manager/Owner)**
- Credentials and API key management
- Team coordination and unblocking
- Git management and PR reviews
- Demo preparation and delivery
- **Guide:** MANAGER_TASKS.md

**Person A (Domain 1 - Email Ingestion)**
- Email webhook from SendGrid
- Attachment extraction and OCR
- Returns IngestedDocument with full text content
- **Guide:** DOMAIN_1_SETUP.md
- **Time Estimate:** 3-4 hours

**Person B (Domain 2 - AI Classification)**
- LLM integration (Cerebras/Groq/Gemini)
- Document classification and field extraction
- Confidence validation and reviewer assignment
- Returns ClassificationResult
- **Guide:** DOMAIN_2_SETUP.md
- **Time Estimate:** 3-4 hours

**Person C (Domain 3 - Box Integration)**
- File routing to correct Box folder
- Metadata application and task creation
- Slack/email notifications
- Returns ProcessingResult
- **Guide:** DOMAIN_3_SETUP.md
- **Time Estimate:** 4-5 hours

---

## Type Contracts (The Boundaries)

### IngestedDocument
**Output of Domain 1 → Input to Domain 2**

```python
@dataclass
class IngestedDocument:
    id: str                     # UUID
    filename: str               # "invoice.pdf"
    content: str                # FULL TEXT (email body + extracted attachments)
    content_type: str           # "application/pdf", "text/plain", etc.
    uploaded_at: datetime       # When ingested
    source: str                 # "email" or "box_file_request"
    email_from: str | None      # Sender email
    file_size_bytes: int | None # File size
```

**Critical:** The `content` field must contain FULL TEXT from email body + extracted attachment text. This is what Domain 2 classifies.

### ClassificationResult
**Output of Domain 2 → Input to Domain 3**

```python
@dataclass
class ClassificationResult:
    document_id: str                    # Reference to IngestedDocument.id
    doc_type: str                       # invoice|contract|resume|receipt|id_document|purchase_order|other
    confidence: float                   # 0.0 to 1.0 (MUST validate!)
    reasoning: str                      # Why this classification
    extracted_fields: dict              # {"vendor": "Acme", "amount": 5000, "date": "2024-05-29"}
    required_reviewer: str | None       # finance|legal|hr|procurement|None
    metadata_tags: list[str]            # ["vendor:acme", "q2_2024", "urgent"]
    classified_at: datetime
```

**Critical:** Confidence MUST be between 0.0 and 1.0. Domain 3 will validate this.

### ProcessingResult
**Output of Domain 3 → API Response**

```python
@dataclass
class ProcessingResult:
    document_id: str                    # Reference to IngestedDocument.id
    box_file_id: str                    # File ID in Box
    destination_folder: str             # "/Invoices/2024/May/"
    status: str                         # "success" | "failure" | "escalated"
    task_id: str | None                 # Box task ID if created
    assigned_to: str | None             # Reviewer email
    metadata_applied: dict              # Metadata tags applied
    notification_sent_to: list[str]     # ["slack", "email"]
    error_message: str | None           # If status="failure"
    completed_at: datetime
```

---

## Implementation Details

### Team Email Setup

- **Team Email:** greenriver.hack.squad@gmail.com (SendGrid forwards emails here)
- **Box Account:** masonsabin@gmail.com (personal account, team accessible)
- **Architecture:** SendGrid receives → Backend processes → Results to Box

### API Keys Required (8 Total)

```
□ SENDGRID_API_KEY           (Domain 1)
□ SENDGRID_VERIFY_TOKEN      (Domain 1)
□ SENDGRID_INBOUND_URL       (ngrok tunnel URL)
□ BOX_CLIENT_ID              (Domain 3)
□ BOX_CLIENT_SECRET          (Domain 3)
□ BOX_ENTERPRISE_ID          (free-developer-account-masonsabin-gmail-com)
□ BOX_DEVELOPER_TOKEN        (Domain 3)
□ CEREBRAS_API_KEY           (Domain 2)
□ GROQ_API_KEY (backup)      (Domain 2 fallback)
```

### Folder Structure in Box

```
/Invoices/{YYYY}/{Month}/      ← invoice documents
/Contracts/{YYYY}/             ← contract documents
/Resumes/                      ← resume documents
/Receipts/{YYYY}/{Month}/      ← receipt documents
/ID_Documents/                 ← identity documents
/Purchases/{YYYY}/             ← purchase orders
/Misc/                         ← other documents
```

### LLM Provider Strategy

**Primary:** Cerebras (fast, free tier, Llama 3.1 8B)  
**Fallback:** Groq (if Cerebras times out or rate limited)  
**Last Resort:** Return escalated status for manual review

---

## Agentic Coding Best Practices Implemented

### 1. Type Contracts as Anti-Hallucination Pattern

Each domain has a strict input/output contract. This prevents hallucination cascades:
- If Domain 2's LLM returns invalid JSON → Domain 2 validates and escalates
- Domain 3 doesn't crash on bad input → it validates against contract
- Each domain can fail independently without breaking downstream

### 2. Deterministic Testing Around Probabilistic LLMs

**What we test:**
- ✅ Structure validation (confidence bounds 0.0-1.0)
- ✅ Error handling (invalid JSON, timeouts)
- ✅ Edge cases (very long documents, unusual formats)

**What we don't test:**
- ❌ LLM accuracy (provider's responsibility)
- ❌ Exact extracted fields (too random)

### 3. Graceful Degradation with Fallbacks

```python
# Domain 2 classification with fallback strategy
try:
    result = await llm_router.call(system_prompt, user_prompt)
    # Validate strictly
    if not (0.0 <= result.confidence <= 1.0):
        raise ValidationError(f"Invalid confidence: {result.confidence}")
    return result
except TimeoutError:
    # Try backup provider (Groq)
    return await fallback_classify(document)
except ValidationError:
    # Escalate if we can't trust the result
    return ClassificationResult(..., status="escalated")
```

### 4. Observable Agentic Systems

Structured logging at every boundary:
```python
logger.info(f"[Domain 2] Classifying {document.filename}")
logger.debug(f"[Domain 2] LLM response received")
logger.info(f"[Domain 2] Classification: {doc_type} ({confidence:.0%})")
logger.warning(f"[Domain 2] Low confidence, escalating")
logger.error(f"[Domain 2] LLM returned invalid JSON")
```

### 5. Provider Flexibility

LLM router abstraction allows swapping providers without changing domain logic:
- Domain 2 doesn't know (or care) if it's using Cerebras, Groq, or Gemini
- Can switch providers by changing `.env` variable
- Can implement provider-specific optimizations in LLMRouter

---

## Pre-Work (What's Already Done)

### Repository Setup
✅ **Safe for any hackathon rules:**
- Project structure and folders
- Type contracts (`backend/shared/types.py`)
- Route endpoints (defined, NOT implemented)
- Test utilities and fixtures
- All documentation and guides

### Box UI Extension (React/TypeScript)
✅ **Ready to build:**
- Manifest.json for Box deployment
- React components (Classification Display, Task Assignment, etc.)
- Professional styling
- API client to backend

### Documentation
✅ **Complete:**
- `GETTING_STARTED.md` - Universal entry point
- `MANAGER_TASKS.md` - Manager's complete guide
- `DOMAIN_1/2/3_SETUP.md` - Role-specific guides with TODOs
- `DEMO_SCRIPT.md` - Word-for-word 5-minute script
- `DEMO_CHECKLIST.md` - Minute-by-minute demo execution
- `docs/SYSTEM_FLOW.md` - Architecture with ASCII diagrams
- `.env.setup.md` - API key setup guide

### Test Data
✅ **Sample documents ready:**
- sample_invoice.txt
- sample_contract.txt
- sample_receipt.txt
- sample_resume.txt
- sample_po.txt
(Convert .txt to PDF before demo)

---

## What Each Team Member Must Implement

### Domain 1 (Person A) - Email Ingestion

**File:** `backend/domain_1_email/service.py`

**TODO Items:**
1. Implement `ingest_email()` - Parse email and extract attachments
2. Implement `validate_sendgrid_signature()` - Verify webhook authenticity
3. Implement webhook handler in `routes.py`
4. Extract text from PDFs (use pdfplumber or pypdf)
5. Make all tests pass: `pytest backend/domain_1_email/tests/ -v`

**Success Criteria:**
- Email webhook receives and processes SendGrid payloads
- Attachments extracted correctly
- IngestedDocument returned with full content
- Tests passing

**Time:** 3-4 hours

### Domain 2 (Person B) - AI Classification

**File:** `backend/domain_2_classifier/service.py`

**TODO Items:**
1. Implement `classify()` - Call LLM and parse response
2. Implement `_parse_llm_response()` - Extract JSON from LLM output
3. Add validation - Confidence 0.0-1.0, doc_type valid
4. Map doc_type to required_reviewer
5. Make all tests pass: `pytest backend/domain_2_classifier/tests/ -v`

**Success Criteria:**
- LLM classification working
- Confidence scores accurate
- Document type correct
- Extracted fields populated
- Tests passing

**Time:** 3-4 hours

### Domain 3 (Person C) - Box Integration

**File:** `backend/domain_3_box_integration/service.py`

**TODO Items:**
1. Implement `process()` - Orchestrate Box integration
2. Route file to correct folder using FOLDER_MAPPING
3. Upload file to Box
4. Apply metadata
5. Create review task
6. Send notifications (Slack + Email)
7. Make all tests pass: `pytest backend/domain_3_box_integration/tests/ -v`

**Success Criteria:**
- File moved to correct folder
- Metadata applied
- Task created and assigned
- Notifications sent
- ProcessingResult returned with all fields
- Tests passing

**Time:** 4-5 hours

---

## Demo Walkthrough

### Five-Minute Script

**[00:00] Introduction (30 seconds)**
- Introduce the problem: Companies receive hundreds of documents
- Introduce the solution: AI-powered classification in Box
- Introduce the architecture: 3 independent domains

**[00:30] System Architecture (45 seconds)**
- Show SYSTEM_FLOW.md diagram
- Point to each domain
- Explain type contracts concept

**[01:15] Live Demo - Send Email (1 minute)**
- Open Gmail
- Send test email with invoice PDF to greenriver.hack.squad@gmail.com
- Watch backend logs show webhook received
- Point out Domain 1 extraction in logs

**[02:15] Show Classification Result (1 minute)**
- Use curl or FastAPI docs to check classification
- Show doc_type: "invoice", confidence: 0.95
- Show extracted fields (vendor, amount, date)

**[03:15] Show Box Integration (1 minute)**
- Open Box account
- Navigate to /Invoices/2024/May/
- Show file with metadata applied
- Show task created and assigned to Finance Manager

**[04:15] Closing Statement (30 seconds)**
- Summarize impact: Automates document routing, saves hours per day
- Mention architecture advantages (parallel work, easy to scale)
- Invite questions

### Fallback Plans

**If backend won't start:**
- Show code and explain architecture
- Show test results proving it works
- Play recorded demo video

**If email webhook fails:**
- Use curl to simulate webhook
- Show same classification result

**If LLM is slow:**
- Have screenshot of expected output saved
- Explain fallback strategy (Groq, escalation)

**If Box file missing:**
- Show backend logs proving upload happened
- Explain Box API worked but file moved

---

## Leadership & Agentic Coding Story

### What Makes This Special

**1. Type Contracts as Anti-Hallucination Pattern**
Traditional architecture: Domain 1 → Domain 2 → Domain 3 (linear)
Our approach: Each domain has strict input/output contracts

When Domain 2's LLM hallucinates:
- It returns invalid JSON
- Domain 2 validates against contract
- Returns escalated status instead of crashing downstream
- Domain 3 never sees bad data

This is how you build resilient AI systems.

**2. Multi-Provider Strategy**
- Primary: Cerebras (fast, free)
- Fallback: Groq (if Cerebras down)
- Last resort: Manual review (if both fail)

Shows we understand LLM APIs aren't magic—they're probabilistic systems that need guardrails.

**3. Observable Agentic Systems**
Structured logging at every boundary:
- Know which provider is being used
- Know when LLM calls fail
- Know when validation fails
- Can debug intelligently

**4. Deterministic Testing Around Probabilistic LLMs**
We don't test "does LLM return 95% confidence" (it's random)
We test:
- Structure validation
- Confidence bounds
- Error handling
- Edge cases

**5. Team Leadership Through Architecture**
Clear type contracts mean:
- Person A doesn't need to know how Domain 2 works
- Person B doesn't need to know how Domain 3 works
- Each person implements to their contract
- Manager removes blockers, doesn't micromanage
- Team works in parallel, no conflicts

---

## Success Metrics

### Technical
- ✅ All 3 domains implement their TODOs
- ✅ Type contracts prevent hallucination cascades
- ✅ All tests passing: `pytest -v`
- ✅ End-to-end flow works (email → classify → Box)
- ✅ Graceful degradation when LLM fails
- ✅ Observable system (structured logs)

### Presentation
- ✅ Demo runs smoothly without major failures
- ✅ Clear explanation of architecture to judges
- ✅ Shows agentic coding best practices
- ✅ Demonstrates team leadership and organization
- ✅ Judges impressed by preparation and execution

### Outcome
- 🏆 Win the hackathon (ambitious but prepared!)
- 🏆 Impress judges with agentic coding knowledge
- 🏆 Demonstrate product management + technical excellence

---

## Timeline

| Time | Milestone | Owner | Status |
|------|-----------|-------|--------|
| Pre-Event | Get API keys | Mason | 🔴 TODO |
| Pre-Event | Create .env file | Mason | 🔴 TODO |
| Pre-Event | Set up ngrok | Mason | 🔴 TODO |
| T+0 | Event starts | Team | ⏳ Waiting |
| T+1h | Demo hour | Team | ⏳ Waiting |
| T+2h | Coding begins | Team | ⏳ Waiting |
| T+8h | Domain 1 complete | Person A | ⏳ Waiting |
| T+10h | Domain 2 complete | Person B | ⏳ Waiting |
| T+12h | Domain 3 complete | Person C | ⏳ Waiting |
| T+14h | Integration testing | Team | ⏳ Waiting |
| T+18h | Demo ready | Mason | ⏳ Waiting |
| T+22h | Final review | Team | ⏳ Waiting |
| T+24h | DEMO TIME | Team | ⏳ Waiting |

---

## Git Strategy

### Branch Structure
```
main
  ├── feature/domain-1-email-ingestion (Person A)
  ├── feature/domain-2-classification (Person B)
  └── feature/domain-3-box-integration (Person C)
```

### Commit Convention
```
[domain-X] Description of change
```

Examples:
- `[domain-1] Implement email webhook handler`
- `[domain-2] Add LLM classification logic`
- `[domain-3] Implement Box file routing`

### PR Process
1. Person implements domain
2. Tests pass locally
3. Create PR
4. Manager reviews
5. Merge when all tests pass
6. Run full `pytest -v` to verify integration

---

## Key Documents Reference

**For the Team:**
- `GETTING_STARTED.md` - Everyone reads this first
- `TEAM_GUIDELINES.md` - Team rules and conventions
- `README.md` - General project overview

**For Specific Roles:**
- `MANAGER_TASKS.md` - Mason's complete guide
- `DOMAIN_1_SETUP.md` - Person A's implementation guide
- `DOMAIN_2_SETUP.md` - Person B's implementation guide
- `DOMAIN_3_SETUP.md` - Person C's implementation guide

**For Demo:**
- `DEMO_SCRIPT.md` - Word-for-word 5-minute script
- `DEMO_CHECKLIST.md` - Minute-by-minute execution guide
- `docs/SYSTEM_FLOW.md` - Architecture diagrams to show judges

**For Technical Understanding:**
- `docs/ARCHITECTURE.md` - Deep dive on system design
- `docs/API_REFERENCE.md` - Endpoint documentation
- `CRISIS_RUNBOOK.md` - Troubleshooting common issues

---

## Questions & Answers

### Why Type Contracts?

**Q: Aren't they overkill for a 24-hour hackathon?**

A: No. Type contracts prevent hallucination cascades from LLMs. If Domain 2's LLM returns invalid JSON, Domain 3 doesn't crash—it validates and escalates. This is how you build resilient AI systems under time pressure.

### Why Not Just One Big Domain?

**Q: Wouldn't it be faster to have one person build everything?**

A: No. Three independent domains let three people work in parallel. With clear contracts, they don't conflict. This is the only way to build a complete system in 24 hours with a 3-person team.

### What If LLM API Goes Down?

**A:** We have a fallback chain:
1. Primary: Cerebras
2. Fallback: Groq
3. Last resort: Escalate to manual review

The system gracefully degrades instead of crashing.

### How Do You Test AI?

**A:** We don't test the LLM's accuracy (provider's job). We test:
- Structure validation (confidence 0.0-1.0)
- Error handling (invalid JSON, timeouts)
- Graceful degradation (fallback providers work)

### What's Your Biggest Risk?

**A:** LLM API reliability. We mitigated it with:
- Provider fallback (Cerebras → Groq → manual)
- Strict response validation
- Timeout handling
- Graceful degradation

---

## Closing Remarks

This is a well-prepared team:
- ✅ Clear architecture with type contracts
- ✅ Role-specific guides for each team member
- ✅ Agentic coding best practices built in
- ✅ Risk mitigation strategies documented
- ✅ Demo materials ready
- ✅ Professional project management

**What matters now:**
1. Mason gets the API keys and shares them
2. Each person reads their domain guide
3. Team codes through the night
4. Everyone passes their tests
5. Demo runs smoothly

**The team is ready. Let's build something amazing.** 🚀

---

## Repository Structure

```
hackathon-skeleton/
├── README_HACKATHON.md          ← Team entry point
├── GETTING_STARTED.md           ← Universal setup
├── MANAGER_TASKS.md             ← Mason's guide
├── DOMAIN_1_SETUP.md            ← Person A's guide
├── DOMAIN_2_SETUP.md            ← Person B's guide
├── DOMAIN_3_SETUP.md            ← Person C's guide
├── DEMO_SCRIPT.md               ← Demo walkthrough
├── DEMO_CHECKLIST.md            ← Demo execution
├── .env.setup.md                ← API key setup
├── CHAT_EXPORT.md               ← This file
│
├── backend/
│   ├── main.py                  ← FastAPI orchestration
│   ├── domain_1_email/          ← TODO: Email ingestion
│   ├── domain_2_classifier/     ← TODO: AI classification
│   ├── domain_3_box_integration/ ← TODO: Box integration
│   └── shared/                  ← Types, config, utilities
│
├── box-extension/               ← React UI (ready to build)
├── test_documents/              ← Sample PDFs
├── docs/                        ← Architecture & guides
└── requirements.txt             ← Python dependencies
```

---

**Created:** May 29, 2026  
**For:** CascadiaJS AI Hackathon 2  
**Team:** Mason (Manager), Person A (Domain 1), Person B (Domain 2), Person C (Domain 3)  
**Status:** ✅ Ready for Launch

🚀 **Good luck tonight!**
