# Domain 2 Setup - AI Classification (Person B)

Welcome! You're implementing the **AI-powered document classification system** that uses an LLM to analyze documents.

---

## Your Mission

**Input:** `IngestedDocument` from Domain 1 (email-extracted text)  
**Output:** `ClassificationResult` with document type, confidence, and extracted fields  
**Time Estimate:** 3-4 hours

---

## What You're Building

```
IngestedDocument (from Domain 1)
    ↓
Your Code (Domain 2)
    ├─ Prepare text for LLM
    ├─ Call LLM API (Cerebras/Groq/Gemini)
    ├─ Parse JSON response
    ├─ Validate confidence and doc_type
    └─ Map doc_type to required reviewer
    ↓
ClassificationResult
    ↓
Domain 3 gets ClassificationResult
```

---

## Files You Own

```
backend/domain_2_classifier/
├── service.py             ← TODO: Implement classification logic
├── llm_router.py          ← Already done (LLM provider abstraction)
├── prompts.py             ← Already done (system prompt for LLM)
├── schemas.py             ← Already done (response schemas)
└── tests/
    └── test_service.py    ← Already done (but YOU make it pass)
```

**Other files (DON'T MODIFY):**
- `backend/shared/types.py` (IngestedDocument input, ClassificationResult output)
- `backend/shared/config.py` (LLM provider config)

---

## Step 1: Understand the Requirements

### What is ClassificationResult? (Your Output)
```python
@dataclass
class ClassificationResult:
    document_id: str                    # Reference to IngestedDocument.id
    doc_type: str                       # invoice|contract|resume|receipt|id_document|purchase_order|other
    confidence: float                   # 0.0 to 1.0 (MUST validate!)
    reasoning: str                      # Why you chose this type (2-3 sentences)
    extracted_fields: dict              # {"vendor": "Acme", "amount": 5000, "date": "2024-05-29"}
    required_reviewer: str | None       # finance|legal|hr|procurement|None
    metadata_tags: list[str]            # ["vendor:acme", "q2_2024", "urgent"]
    classified_at: datetime             # When classified
```

### What the LLM Will Return
```json
{
  "doc_type": "invoice",
  "confidence": 0.95,
  "reasoning": "Document contains invoice header, line items, and total amount.",
  "extracted_fields": {
    "vendor": "Acme Corp",
    "amount": 5000,
    "date": "2024-05-29"
  },
  "required_reviewer": "finance",
  "metadata_tags": ["vendor:acme", "q2_2024", "urgent"]
}
```

### Reviewer Mapping (Use This!)
```python
REVIEWER_MAPPING = {
    "invoice": "finance",
    "contract": "legal",
    "resume": "hr",
    "receipt": "procurement",
    "id_document": "hr",
    "purchase_order": "procurement",
    "other": None
}
```

---

## Step 2: How to Call the LLM

The `LLMRouter` is already implemented. Use it like this:

```python
from backend.domain_2_classifier.llm_router import LLMRouter

router = LLMRouter()

response = await router.call(
    system_prompt="You are a document classifier...",
    user_prompt="Please classify this document: <document text here>"
)
# Returns: str (the LLM's response, should be JSON)
```

**It handles:**
- ✅ Provider selection (Cerebras, Groq, Gemini)
- ✅ API calls with retries
- ✅ Error handling
- ✅ Fallback providers if one fails

**You provide:**
- ✅ System prompt (in `prompts.py`, already written!)
- ✅ User prompt (you create this from the document)

---

## Step 3: Look at the TODO Comments

**In `service.py`, line 20-44:**
```python
async def classify(self, document: IngestedDocument) -> ClassificationResult:
    """
    TODO: Implement classification logic:
    1. Get document text from IngestedDocument.content
    2. Call self.llm_router.call() with system and user prompts
    3. Parse JSON response from LLM
    4. Validate confidence is 0.0-1.0
    5. Map doc_type to required_reviewer using REVIEWER_MAPPING
    6. Create ClassificationResult with all fields
    7. Log classification result
    8. Return ClassificationResult
    """
    raise NotImplementedError("TODO: Implement LLM-based classification")
```

---

## Step 4: Implementation Checklist

### Phase 1: Basic LLM Call (1 hour)
- [ ] In `service.py`, implement `classify()`:
  - [ ] Get document text from `document.content`
  - [ ] Create user prompt with document text (first 10k chars)
  - [ ] Call `self.llm_router.call()` with system + user prompt
  - [ ] Get response (should be JSON string)
  - [ ] Return a dummy ClassificationResult (hardcoded for now)

### Phase 2: Parse LLM Response (1 hour)
- [ ] Implement `_parse_llm_response()`:
  - [ ] Parse JSON from LLM response
  - [ ] Extract: doc_type, confidence, reasoning, extracted_fields, required_reviewer, metadata_tags
  - [ ] Handle parsing errors (LLM might return bad JSON)
  - [ ] Return parsed dict

### Phase 3: Validation & Mapping (1 hour)
- [ ] Still in `classify()`, add validation:
  - [ ] Check `confidence` is between 0.0 and 1.0
  - [ ] Check `doc_type` is in allowed list
  - [ ] Map `doc_type` to `required_reviewer` using REVIEWER_MAPPING
  - [ ] Raise error if validation fails

### Phase 4: Create Result Object (30 min)
- [ ] Create `ClassificationResult` with all fields:
  - [ ] `document_id` from `document.id`
  - [ ] `doc_type`, `confidence`, `reasoning` from LLM
  - [ ] `extracted_fields` from LLM
  - [ ] `required_reviewer` from mapping
  - [ ] `metadata_tags` from LLM
  - [ ] `classified_at` = now
- [ ] Log the result
- [ ] Return it

### Phase 5: Testing (30 min)
- [ ] Make Domain 2 tests pass:
  ```bash
  pytest backend/domain_2_classifier/tests/ -v
  ```

---

## Step 5: Important Notes

### System Prompt (Already Written!)
In `prompts.py`:
```python
CLASSIFICATION_SYSTEM_PROMPT = """You are a document classification expert...
Respond with valid JSON only, no additional text.
Document types: invoice, contract, resume, receipt, id_document, purchase_order, other
...
"""
```

Just use it as-is! It's already optimized.

### User Prompt Template
Create something like:
```python
def get_classification_prompt(document_text: str) -> str:
    return f"""Please classify the following document:

{document_text[:10000]}  # First 10k chars

Respond with JSON format: {{"doc_type": "...", "confidence": 0.95, ...}}"""
```

### Error Handling
The LLM might:
- ❌ Return invalid JSON
- ❌ Return missing fields
- ❌ Return confidence > 1.0 or < 0.0
- ❌ Crash (timeout, rate limit)

Handle gracefully:
```python
try:
    response = await self.llm_router.call(...)
    parsed = self._parse_llm_response(response)
    # Validate...
except json.JSONDecodeError:
    # Log and raise ClassificationError
    raise ClassificationError("LLM returned invalid JSON")
except KeyError as e:
    # Log missing field
    raise ClassificationError(f"Missing field in LLM response: {e}")
```

### Confidence Validation
```python
if not (0.0 <= parsed["confidence"] <= 1.0):
    raise InvalidClassificationResultError(
        f"Confidence {parsed['confidence']} not in [0.0, 1.0]"
    )
```

---

## Step 6: Testing Your Work

### Manual Testing
```python
# Create test document
from backend.shared.types import IngestedDocument

doc = IngestedDocument(
    id="test-123",
    filename="invoice.pdf",
    content="Invoice from Acme Corp for $5000, dated May 29, 2024",
    content_type="application/pdf",
    source="email"
)

# Classify it
from backend.domain_2_classifier.service import ClassificationService

service = ClassificationService()
result = await service.classify(doc)

# Should see:
print(result.doc_type)      # "invoice"
print(result.confidence)    # 0.95 (or similar)
print(result.extracted_fields)  # {"vendor": "Acme Corp", "amount": 5000, ...}
```

### Unit Testing
```bash
# Run Domain 2 tests
pytest backend/domain_2_classifier/tests/ -v

# Run specific test
pytest backend/domain_2_classifier/tests/test_service.py::test_classify_invoice -v

# Run with coverage
pytest backend/domain_2_classifier/ --cov=backend.domain_2_classifier -v
```

---

## Step 7: Hand Off to Domain 3

When your tests pass, Domain 3 will use your `ClassificationResult` to route files.

**What Domain 3 Needs:**
- [ ] `doc_type` is one of: invoice, contract, resume, receipt, id_document, purchase_order, other
- [ ] `confidence` is between 0.0 and 1.0 (float)
- [ ] `extracted_fields` has relevant data (vendor, amount, date, etc.)
- [ ] `required_reviewer` is set (finance, legal, hr, procurement, or None)
- [ ] `metadata_tags` are descriptive

**Example of Good Output:**
```python
ClassificationResult(
    document_id="doc-uuid-123",
    doc_type="invoice",
    confidence=0.95,
    reasoning="Document contains invoice header, line items, and total amount.",
    extracted_fields={
        "vendor": "Acme Corp",
        "amount": 5000,
        "date": "2024-05-29",
        "invoice_number": "INV-12345"
    },
    required_reviewer="finance",
    metadata_tags=["vendor:acme", "q2_2024", "urgent"],
    classified_at=datetime.now()
)
```

---

## Helpful Resources

**In the repo:**
- `backend/domain_2_classifier/prompts.py` - System prompt (already written!)
- `backend/domain_2_classifier/llm_router.py` - How to call LLM
- `backend/shared/types.py` - ClassificationResult definition
- `backend/shared/config.py` - REVIEWER_MAPPING
- `backend/shared/fixtures.py` - Test data helpers
- `AGENT_DOMAIN_2_CLASSIFIER.md` - Detailed domain guide

**External:**
- Cerebras API: https://docs.cerebras.ai
- Groq API: https://console.groq.com/docs
- JSON parsing: https://docs.python.org/3/library/json.html

---

## Troubleshooting

**LLM returning invalid JSON?**
1. Check your user prompt is clear
2. Try with a simpler document first
3. Look at LLM logs to see what it returned
4. Try different provider (Groq if Cerebras failing)

**Confidence validation failing?**
1. The LLM returned number > 1.0 or < 0.0
2. Add bounds checking: `min(1.0, max(0.0, confidence))`
3. Or raise error if out of bounds

**Tests failing?**
1. Check fixtures in `backend/shared/fixtures.py`
2. Make sure you're returning `ClassificationResult`, not dict
3. Look at test error message - it's usually helpful
4. Ask the team!

---

## Success Criteria

Your domain is **DONE** when:

- [ ] `pytest backend/domain_2_classifier/tests/ -v` shows all passing ✅
- [ ] Classification works with real LLM (Cerebras/Groq)
- [ ] Confidence scores are accurate (0.0-1.0)
- [ ] Doc types are correct (invoice, contract, etc.)
- [ ] Extracted fields are populated
- [ ] Reviewer mapping works (finance, legal, etc.)
- [ ] No `NotImplementedError` anywhere in your code
- [ ] You can classify a test document by hand and explain why

---

## Time Management

```
Hour 0-1:   Read this, understand requirements
Hour 1-2:   Implement basic classify() + LLM call
Hour 2-3:   Parse LLM response + validation
Hour 3-4:   Create ClassificationResult + error handling
Hour 4-4.5: Write tests, make them pass
Hour 4.5-5: Celebrate! You're done! 🎉
```

Don't overthink the LLM prompt. The system prompt is already great.

---

**You've got this! Go build! 🚀**

Questions? Ask the team on Discord/Slack or check CRISIS_RUNBOOK.md
