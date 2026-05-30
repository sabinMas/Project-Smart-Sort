# Box Smart Inbox

An AI-powered document intake, classification, and routing system that integrates with Box.

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- API keys:
  - SendGrid (email ingestion)
  - Cerebras/Groq/Gemini (AI classification)
  - Box (file management)

### Setup

1. **Clone and enter directory**
   ```bash
   git clone <repo>
   cd hackathon-skeleton
   ```

2. **Copy environment template**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Create virtual environment (optional, Docker handles this)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run with Docker**
   ```bash
   docker-compose up
   # FastAPI available at http://localhost:8000
   # Swagger docs at http://localhost:8000/docs
   ```

   Or run locally:
   ```bash
   uvicorn backend.main:app --reload
   ```

6. **Run tests**
   ```bash
   pytest -v                           # All tests
   pytest domain_1_email/ -v           # Domain 1 tests
   pytest domain_2_classifier/ -v      # Domain 2 tests
   pytest domain_3_box_integration/ -v # Domain 3 tests
   pytest tests/test_integration.py -v # End-to-end tests
   ```

## Architecture

```
Email/Upload
    ↓
[Domain 1: Email Ingestion]
    ↓ IngestedDocument
[Domain 2: AI Classification]
    ↓ ClassificationResult
[Domain 3: Box Integration]
    ↓ ProcessingResult
[Notifications] → Slack, Email, Dashboard
```

### Three Independent Domains

1. **Domain 1: Email Ingestion** (`domain_1_email/`)
   - Receives emails from SendGrid webhook
   - Extracts attachments and content
   - Returns IngestedDocument

2. **Domain 2: AI Classification** (`domain_2_classifier/`)
   - Accepts IngestedDocument
   - Classifies with Llama 3.1 8B (Cerebras)
   - Returns ClassificationResult with doc type and extracted fields

3. **Domain 3: Box Integration** (`domain_3_box_integration/`)
   - Accepts ClassificationResult
   - Moves file to correct folder
   - Applies metadata, creates review task
   - Sends notifications

## Key Endpoints

```
GET  /health                    # Health check
POST /webhooks/email            # Email webhook (Domain 1)
POST /documents/intake          # End-to-end processing
GET  /status                    # Processing statistics
GET  /documents/{document_id}   # Document status
```

## Project Structure

```
backend/
├── domain_1_email/              # Email ingestion
│   ├── routes.py                # FastAPI endpoints
│   ├── service.py               # Business logic
│   ├── models.py                # Pydantic models
│   └── tests/                   # Unit tests
│
├── domain_2_classifier/         # AI classification
│   ├── llm_router.py            # LLM provider abstraction
│   ├── service.py               # Classification logic
│   ├── prompts.py               # LLM prompts
│   └── tests/
│
├── domain_3_box_integration/    # Box integration
│   ├── box_client.py            # Box SDK wrapper
│   ├── tasks.py                 # Task creation
│   ├── metadata.py              # Metadata management
│   ├── notifications.py         # Slack/email notifications
│   ├── service.py               # Orchestration
│   └── tests/
│
├── shared/
│   ├── types.py                 # Shared types (LOCKED)
│   ├── config.py                # Environment config
│   ├── errors.py                # Custom exceptions
│   ├── logging.py               # Logging setup
│   └── fixtures.py              # Test fixtures
│
├── main.py                      # FastAPI app + orchestration
├── tests/                       # Integration tests
└── requirements.txt             # Dependencies
```

## Development

### Rules for Team Members

1. **Domain Isolation**: Each person works in their domain only
   - Domain 1: Only edit `domain_1_email/`
   - Domain 2: Only edit `domain_2_classifier/`
   - Domain 3: Only edit `domain_3_box_integration/`

2. **Type Contracts**: Respect shared types in `shared/types.py`
   - IngestedDocument (output of Domain 1)
   - ClassificationResult (output of Domain 2)
   - ProcessingResult (output of Domain 3)

3. **No Cross-Domain Imports**: Never import between domains
   - ✅ OK: `from backend.shared.types import IngestedDocument`
   - ❌ NO: `from backend.domain_2_classifier.service import ClassificationService`

4. **Testing**: Each domain has unit tests with mocks
   - Use fixtures in `shared/fixtures.py`
   - Test your domain in isolation

### Git Workflow

```bash
# Create domain-specific branch
git checkout -b feature/domain-1-email

# Make changes and test
git add domain_1_email/
git commit -m "[domain-1] Add SendGrid webhook handler"

# Push and create PR
git push origin feature/domain-1-email

# Key rule: One domain per PR, no cross-domain changes
```

## Demo Checklist

### Pre-Demo
- [ ] All tests passing: `pytest -v`
- [ ] Docs built and viewable
- [ ] 5 sample documents prepared
- [ ] Demo script ready

### Demo Flow
1. Send test email with invoice PDF
2. Show document classified as "invoice" with 95%+ confidence
3. Verify file moved to `/Invoices/2024/May` in Box
4. Show task created and assigned to finance team
5. Display Slack notification sent
6. Show audit trail in logs

## Troubleshooting

### LLM Provider Not Responding
```bash
# Edit .env: Switch provider
LLM_PROVIDER=cerebras  # Try groq if cerebras down
# Restart server
```

### Box Authentication Fails
```bash
# Check Box keys in .env
# Verify enterprise ID
# Regenerate OAuth token if needed
```

### Merge Conflicts
```bash
# Most conflicts are in main.py when integrating domains
# Just add both imports and run tests
git add main.py
git commit -m "Resolve merge conflict: add Domain X imports"
pytest -v  # Verify tests pass
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [API Reference](docs/API_REFERENCE.md) - Endpoint documentation
- [Crisis Runbook](docs/CRISIS_RUNBOOK.md) - Troubleshooting guide
- [Team Guidelines](TEAM_GUIDELINES.md) - Rules for working together
- [Agent Guides](AGENT_DOMAIN_1_EMAIL.md) - Domain-specific instructions

## Team Members

- **Person A** (Domain 1): Email Ingestion
- **Person B** (Domain 2): AI Classification
- **Person C** (Domain 3): Box Integration
- **Product Owner**: Main orchestration, merges, decisions

## Success Metrics

- Classification accuracy: ≥85%
- Extraction accuracy: ≥90%
- End-to-end latency: <3 seconds
- All tests passing
- Demo working without issues

## Support

For issues or questions:
1. Check [Crisis Runbook](docs/CRISIS_RUNBOOK.md)
2. Review [Team Guidelines](TEAM_GUIDELINES.md)
3. Look at domain-specific guide files (AGENT_DOMAIN_*.md)

---

Built for a 24-hour hackathon. Good luck! 🚀
