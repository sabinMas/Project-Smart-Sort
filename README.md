# 📥 Box Smart Inbox

**AI-powered document intake, classification, and routing for [Box](https://www.box.com/).**
Drop a PDF in a folder (or email it in) and watch it get read, understood, filed, tagged, and routed to the right reviewer — automatically.

> Built at the **CascadiaJS AI Hackathon**. Powered by Cerebras inference, Box, and FastAPI.

---

## 🎬 Demo

<!-- TEAMMATE: paste the video URL between the parentheses below and delete this comment -->
**▶️ [Watch the 3-minute demo](DEMO_VIDEO_URL_HERE)**

<!-- Optional: drop a screenshot/GIF in docs/ and point to it here, e.g. ![Smart Inbox in action](docs/demo.gif) -->
<!-- SCREENSHOT_PLACEHOLDER -->

See a PDF land in Box, get classified by Cerebras in well under a second, route itself into the right folder, and fire a Slack alert — end to end, no clicks.

---

## The Problem

Knowledge workers drown in unstructured documents. Invoices, contracts, receipts, and resumes pile up in shared inboxes and "miscellaneous" folders, then someone has to manually open each one, figure out what it is, rename it, file it, and tell the right person to review it. It's slow, error-prone, and nobody's favorite part of the job.

## The Solution

Box Smart Inbox turns that whole chore into a zero-click pipeline:

```
   📧 Email a PDF          📤 Or upload to Box
         │                        │
         └───────────┬────────────┘
                     ▼
            ┌──────────────────┐
            │  Box /Inbox       │  ← file lands here
            └──────────────────┘
                     │  FILE.UPLOADED webhook (or 60s poller)
                     ▼
   ┌─────────────────────────────────────────────┐
   │  1. Extract text   (Textract → pdfplumber)   │
   │  2. Classify       (Cerebras gpt-oss-120b)   │
   │  3. Route          (move to typed folder)    │
   │  4. Tag            (apply Box metadata)       │
   │  5. Assign         (create review task)      │
   │  6. Notify         (Slack message)           │
   └─────────────────────────────────────────────┘
                     ▼
   /Invoices/2026/March   /Contracts/...   /Resumes/...
```

A 15-page contract emailed to your inbox shows up filed under `/Contracts`, tagged, assigned to legal, with a Slack ping — in seconds, no human in the loop.

---

## ✨ Features

- **Zero-click ingestion** — Email a document or upload it to Box; a `FILE.UPLOADED` webhook (with a 60s polling fallback) picks it up automatically.
- **Fast AI classification** — Uses Cerebras `gpt-oss-120b` for low-latency inference, with Groq and Gemini available as configurable alternate providers. Classifies into invoice, contract, resume, receipt, ID document, purchase order, or other.
- **Field extraction** — Pulls structured fields (vendor, amount, invoice number, dates, etc.) straight out of the document text.
- **Smart routing** — Moves the original file into the correct Box folder, auto-creating `Year/Month` subfolders for financial documents.
- **Metadata tagging** — Applies Box metadata so documents are searchable by type, confidence, vendor, and more.
- **Reviewer assignment** — Creates a Box review task and assigns it to the right team (finance, legal, HR, procurement).
- **Slack notifications** — Posts a rich message with the document type, confidence, extracted fields, and a working link back to the Box file.
- **Box UI Extension** — A React sidebar that shows classification results and lets reviewers act without leaving Box.
- **Signature tracking** — A DocuSign-shaped workflow that records envelope and recipient state and processes DocuSign webhook events. (Live envelope sending is scaffolded; the send path currently creates tracking records rather than calling the DocuSign API.)
- **Resilient by design** — Retry with exponential backoff on the classification call, a `DEMO_MODE` that runs the whole pipeline without live credentials, and non-fatal degradation (a failed metadata, task, or Slack step never blocks the file from being filed).

---

## 🏗️ Architecture

The backend is organized into three independent domains that communicate only through shared type contracts — no cross-domain imports. This keeps each stage testable in isolation and easy to reason about.

```
backend/
├── domain_1_email/            # Ingestion: SendGrid/Postmark webhooks, PDF text extraction
│   ├── routes.py              #   email + upload endpoints
│   ├── service.py             #   ingestion logic
│   └── textract_parser.py     #   AWS Textract → pdfplumber fallback
│
├── domain_2_classifier/       # AI: classify + extract fields
│   ├── llm_router.py          #   provider abstraction (Cerebras / Groq / Gemini, set by LLM_PROVIDER)
│   ├── prompts.py             #   classification prompts
│   └── service.py             #   parse + validate LLM output
│
├── domain_3_box_integration/  # Box: route, tag, assign, notify, sign
│   ├── box_client.py          #   Box SDK wrapper
│   ├── routes.py              #   webhooks (Box/DocuSign), inbox processing
│   ├── metadata.py            #   Box metadata management
│   ├── tasks.py               #   review-task assignment
│   ├── notifications.py       #   Slack notifications
│   └── approval_service.py    #   approval + signature flow
│
├── orchestration/             # Chains domain 1 → 2 → 3 end-to-end
├── shared/                    # Type contracts, config, db, logging, errors
└── main.py                    # FastAPI app + background inbox poller

box-extension/                 # React + Vite + TypeScript Box UI Extension
```

### The type contracts

Domains hand off via three locked Pydantic models in `backend/shared/types.py`:

| Stage | Output | Carries |
|-------|--------|---------|
| Domain 1 → 2 | `IngestedDocument` | filename, extracted text, source, raw bytes |
| Domain 2 → 3 | `ClassificationResult` | doc type, confidence, extracted fields, reviewer, tags |
| Domain 3 → API | `ProcessingResult` | Box file id, destination folder, task id, assignee, status |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Inference** | Cerebras `gpt-oss-120b` (primary); Groq Llama 3.1 70B + Google Gemini selectable via `LLM_PROVIDER` |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| **Document I/O** | Box SDK, AWS Textract, pdfplumber / PyPDF2 |
| **Storage** | PostgreSQL (asyncpg); Redis container included for future async queue use |
| **Ingestion** | SendGrid / Postmark inbound email webhooks |
| **Signatures** | DocuSign |
| **Notifications** | Slack incoming webhooks |
| **Frontend** | React 18, Vite, TypeScript (Box UI Extension) |
| **Deployment** | Docker / Docker Compose (backend), Vercel (frontend) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- A [Box developer app](https://developer.box.com/) (Client ID + Secret + Enterprise ID)
- A [Cerebras](https://cloud.cerebras.ai/) API key (or Groq / Gemini)
- Optional: SendGrid (email-in), Slack webhook URL, AWS credentials (Textract), DocuSign

### 1. Clone and configure

```bash
git clone https://github.com/sabinMas/Project-Smart-Sort.git
cd Project-Smart-Sort
cp .env.example .env      # then fill in your keys — see .env.setup.md
```

### 2. Run with Docker (recommended)

```bash
docker-compose up
```

- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs

### 3. Or run locally

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### 4. Try it

Drop a PDF into your configured Box Inbox folder (or POST one to the API), and watch the logs sort it:

```bash
# Sort everything currently sitting in the Box Inbox folder
curl -X POST http://localhost:8000/api/process-inbox

# Or upload a document directly
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Content-Type: application/json" \
  -d '{"file_name": "invoice.pdf", "file_data": "<base64-encoded-pdf>"}'
```

---

## ⚙️ Configuration

Key environment variables (see `.env.example` and `.env.setup.md` for the full list):

| Variable | Purpose |
|----------|---------|
| `LLM_PROVIDER` | `cerebras` (default), `groq`, or `gemini` |
| `CEREBRAS_API_KEY` | Cerebras inference key |
| `BOX_CLIENT_ID` / `BOX_CLIENT_SECRET` / `BOX_ENTERPRISE_ID` | Box app credentials |
| `BOX_INBOX_FOLDER_ID` | Folder the poller watches; enables auto-sort |
| `SENDGRID_API_KEY` | Inbound email parsing |
| `SLACK_WEBHOOK_URL` | Slack notifications (see `SLACK_WEBHOOK_SETUP.md`) |
| `USE_TEXTRACT` + `AWS_*` | Enable AWS Textract extraction |
| `DATABASE_URL` | PostgreSQL connection string |
| `DEMO_MODE` | Skip DB connection and serve realistic demo data |

---

## 📡 Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Health check |
| `GET`  | `/status` | Pipeline stats (documents processed, success rate) |
| `POST` | `/webhooks/box` | Box `FILE.UPLOADED` → auto classify & sort |
| `POST` | `/webhooks/sendgrid` | Inbound email → ingest, classify, route |
| `POST` | `/api/process-inbox` | Sort all PDFs currently in the Box Inbox |
| `POST` | `/api/documents/upload` | Upload a document directly (base64) |
| `POST` | `/api/approvals/review` | Submit a human review decision |
| `POST` | `/api/signatures/send` | Open a signature-tracking envelope (DocuSign-shaped) |
| `POST` | `/webhooks/docusign` | DocuSign envelope events |
| `GET`  | `/api/documents` | List processed documents with filters |
| `GET`  | `/api/documents/{id}` | Get a single document's pipeline status |

> Classification runs automatically inside the Box, email, and inbox-processing pipelines via the orchestrator. The standalone `/api/classify` and `/api/contacts/*` routes are scaffolded but not yet implemented.

Full reference: [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md).

---

## 🧪 Testing

```bash
pytest -v                                   # full suite
pytest backend/domain_1_email/ -v           # email ingestion
pytest backend/domain_2_classifier/ -v      # AI classification
pytest backend/domain_3_box_integration/ -v # Box integration
pytest backend/tests/test_integration.py -v # end-to-end
```

Each domain has unit tests with mocked external services, so the suite runs without live API keys.

---

## 📦 Deployment

- **Backend** — Containerized via the included `Dockerfile` / `docker-compose.yml` (FastAPI + Redis). Point the Box webhook at your public `/webhooks/box` URL (use ngrok for local demos).
- **Frontend** — The Box UI Extension builds with Vite and deploys to Vercel (`vercel.json` is preconfigured). See [`VERCEL_DEPLOYMENT.md`](VERCEL_DEPLOYMENT.md).

---

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) — system design and data flow
- [System Flow](docs/SYSTEM_FLOW.md) — visual end-to-end diagrams
- [API Reference](docs/API_REFERENCE.md) — endpoint details
- [Slack Setup](SLACK_WEBHOOK_SETUP.md) — wiring up notifications
- [Crisis Runbook](docs/CRISIS_RUNBOOK.md) — troubleshooting

---

## 🔭 Roadmap

- Extend confidence-gated review (already in the email/orchestrator path, threshold 0.80) to the Box webhook and inbox-poller paths
- Live DocuSign envelope sending (signature tracking and webhook handling are already in place)
- Implement the standalone `/api/classify` and contact-verification endpoints
- Wire the included Redis container into an async processing queue
- Full dashboard view of the processing pipeline

---

Built with care for the CascadiaJS AI Hackathon. 🚀
