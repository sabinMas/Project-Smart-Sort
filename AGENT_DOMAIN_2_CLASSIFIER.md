# Agent Domain 2: AI Classification

**For:** Person B (AI Classification)  
**Estimated Time:** 3-4 hours  
**Critical Success:** Return `ClassificationResult` with valid doc_type and confidence score (0.0-1.0)

---

## Your Mission

Accept `IngestedDocument` from Domain 1 → Call LLM (Llama 3.1 8B) → Extract metadata → Return `ClassificationResult`.

You're the intelligence layer. Classify documents with high accuracy and extract meaningful data.

## Your Files

You own everything in `backend/domain_2_classifier/`:

```
domain_2_classifier/
├── __init__.py           (Already created)
├── schemas.py            (Complete: Pydantic models)
├── llm_router.py         (TODO: Route between LLM providers)
├── service.py            (TODO: Classification logic)
├── prompts.py            (Complete: System/user prompts)
└── tests/
    ├── __init__.py       (Already created)
    └── test_service.py   (TODO: Classification tests)
```

**DO NOT EDIT:**
- `backend/domain_1_email/` (Person A's domain)
- `backend/domain_3_box_integration/` (Person C's domain)
- `backend/main.py` (PO's file)
- `backend/shared/types.py` (LOCKED contract)

## Input: IngestedDocument

From Domain 1 (Person A):

```python
IngestedDocument(
    id="550e8400-e29b-41d4-a716-446655440000",
    filename="ACME_Invoice_2024.pdf",
    content="Full invoice text...",  # Complete text from email/PDF
    content_type="application/pdf",
    uploaded_at=datetime(...),
    source="email",
    email_from="vendor@acme.com",
    file_size_bytes=45230,
)
```

## Output: ClassificationResult

You must return this object:

```python
from backend.shared.types import ClassificationResult

ClassificationResult(
    document_id="550e8400-e29b-41d4-a716-446655440000",  # From input
    doc_type="invoice",  # One of: invoice, contract, resume, receipt, id_document, purchase_order, other
    confidence=0.98,  # MUST be float 0.0 to 1.0
    reasoning="Contains invoice header, itemized services, total amount, and payment terms typical of business invoices.",
    extracted_fields={
        "vendor": "ACME Corporation",
        "amount": 5000.00,
        "invoice_number": "INV-2024-05-001",
        "date": "2024-05-15",
    },
    required_reviewer="finance",  # finance, legal, hr, procurement, or None
    metadata_tags=["vendor:acme", "amount:5000", "q2_2024"],
    classified_at=datetime.now(),
)
```

**Most Critical:**
- `confidence` must be 0.0 to 1.0 (float, not percentage)
- `doc_type` must be one of the 7 valid types
- `reasoning` must explain the choice

## Implementation Roadmap

### Step 1: Implement llm_router.py (45 min)

Router that switches between LLM providers:

```python
# domain_2_classifier/llm_router.py

class CerebasProvider(LLMProvider):
    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        TODO:
        1. Use anthropic.Anthropic() or appropriate Cerebras client
        2. Call Llama 3.1 8B model
        3. Return JSON response as string
        """
        pass

class GroqProvider(LLMProvider):
    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        TODO:
        1. Use groq.Groq() client
        2. Call mixtral or llama model
        3. Return JSON response as string
        """
        pass

class GeminiProvider(LLMProvider):
    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        TODO:
        1. Use google.generativeai client
        2. Call Gemini model
        3. Return JSON response as string
        """
        pass

class LLMRouter:
    def __init__(self):
        # Select provider based on Config.LLM_PROVIDER
        self.provider = self._get_provider()
    
    async def call(self, system_prompt: str, user_prompt: str) -> str:
        # Route to selected provider
        return await self.provider.call(system_prompt, user_prompt)
```

**Test it:**
```python
router = LLMRouter()
response = await router.call(system_prompt, user_prompt)
# Should return valid JSON string
```

### Step 2: Implement service.py (2-3 hours)

Core classification logic:

```python
# domain_2_classifier/service.py

from backend.domain_2_classifier.prompts import (
    CLASSIFICATION_SYSTEM_PROMPT,
    get_classification_prompt
)

class ClassificationService:
    def __init__(self):
        self.llm_router = LLMRouter()
    
    async def classify(self, document: IngestedDocument) -> ClassificationResult:
        """
        TODO:
        1. Get system prompt from prompts.py
        2. Create user prompt with document content (first 10k chars)
        3. Call llm_router.call(system_prompt, user_prompt)
        4. Parse JSON response using _parse_llm_response()
        5. Validate confidence 0.0-1.0
        6. Map doc_type to required_reviewer
        7. Create and return ClassificationResult
        8. Log the classification
        """
        pass
    
    def _parse_llm_response(self, response: str) -> dict:
        """
        TODO:
        1. Extract JSON from LLM response (might have extra text)
        2. Parse JSON
        3. Validate required fields:
           - doc_type (valid value)
           - confidence (0.0-1.0)
           - reasoning (non-empty)
           - extracted_fields (dict)
           - metadata_tags (list)
        4. Return parsed dict
        5. Raise InvalidClassificationResultError if invalid
        """
        pass
    
    def _validate_confidence(self, confidence: float) -> bool:
        """Validate confidence is in [0.0, 1.0]"""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        return True
```

**Key details:**
- Prompts are provided in `prompts.py` - just use them
- `CLASSIFICATION_SYSTEM_PROMPT` tells LLM what to do
- `get_classification_prompt()` inserts document text
- LLM response is JSON - parse and validate it

### Step 3: Add Tests (30-45 min)

```python
# domain_2_classifier/tests/test_service.py

@pytest.mark.asyncio
async def test_classify_invoice():
    service = ClassificationService()
    # Use provided fixture
    result = await service.classify(MOCK_INGESTED_DOCUMENT_INVOICE)
    
    assert isinstance(result, ClassificationResult)
    assert result.doc_type == "invoice"
    assert 0.0 <= result.confidence <= 1.0
    assert result.required_reviewer == "finance"
    assert "vendor" in result.extracted_fields

@pytest.mark.asyncio
async def test_classify_contract():
    service = ClassificationService()
    result = await service.classify(MOCK_INGESTED_DOCUMENT_CONTRACT)
    
    assert result.doc_type == "contract"
    assert result.required_reviewer == "legal"

def test_validate_confidence_valid():
    service = ClassificationService()
    assert service._validate_confidence(0.95) == True

def test_validate_confidence_invalid():
    service = ClassificationService()
    with pytest.raises(ValueError):
        service._validate_confidence(1.5)
```

## LLM Details

### Which LLM?

Primary: **Cerebras Llama 3.1 8B**
- Cheap and fast
- Good for document classification
- Runs on Cerebras infrastructure

Fallback: **Groq**
- Also very fast
- Good alternative if Cerebras down

Fallback: **Google Gemini**
- Last resort

### Prompt Structure

You have system and user prompts in `prompts.py`:

```python
CLASSIFICATION_SYSTEM_PROMPT = """You are a document classification expert...
Classify documents into: invoice, contract, resume, receipt, id_document, purchase_order, other
Return JSON with: doc_type, confidence, reasoning, extracted_fields, required_reviewer, metadata_tags"""

def get_classification_prompt(document_text: str) -> str:
    return f"""Classify this document:
    
    {document_text[:10000]}  # First 10k chars only
    
    Respond with JSON only."""
```

Just use these. They're already tuned.

### Expected JSON Response

```json
{
  "doc_type": "invoice",
  "confidence": 0.98,
  "reasoning": "Contains invoice header, itemized services, total amount, and payment terms...",
  "extracted_fields": {
    "vendor": "ACME Corporation",
    "amount": 5000.00,
    "invoice_number": "INV-2024-05-001",
    "date": "2024-05-15"
  },
  "required_reviewer": "finance",
  "metadata_tags": ["vendor:acme", "q2_2024", "amount:5000", "urgent"]
}
```

## Dependencies You'll Need

Already in requirements.txt:
- `anthropic` - For Cerebras (Claude API)
- `groq` - For Groq LLM
- `google-generativeai` - For Gemini

## Document Types & Reviewers

| Type | Primary Reviewer | Clues |
|------|------------------|-------|
| invoice | finance | Vendor, amount, invoice #, due date |
| contract | legal | Parties, terms, signatures, consideration |
| resume | hr | Experience, education, skills, contact |
| receipt | finance | Purchase, items, total, date |
| id_document | hr | ID number, expiry, government issued |
| purchase_order | procurement | PO number, supplier, items, cost |
| other | None | Doesn't fit other categories |

## Testing Before Handoff

```bash
# Run only your tests
pytest domain_2_classifier/ -v

# Verify no cross-domain imports
grep -r "from backend.domain_" domain_2_classifier/
# Should return: 0 matches

# Check nothing broke
pytest -v
```

## Common Pitfalls & Solutions

### Pitfall 1: Confidence Score Invalid
**Symptom:** `confidence: 95` or `confidence: 1.5`  
**Problem:** LLM returning percentage or exceeding bounds  
**Solution:** Validate and clamp in `_parse_llm_response()`:
```python
confidence = float(parsed["confidence"])
if confidence > 1.0 and confidence > 100:
    confidence = confidence / 100  # Convert 95 → 0.95
confidence = min(1.0, max(0.0, confidence))  # Clamp to [0, 1]
```

### Pitfall 2: JSON Parsing Fails
**Symptom:** "Invalid JSON from LLM"  
**Problem:** LLM adds extra text around JSON  
**Solution:** Extract JSON:
```python
import json
import re
# Try to extract JSON from response
json_match = re.search(r'\{.*\}', response, re.DOTALL)
if json_match:
    return json.loads(json_match.group())
```

### Pitfall 3: LLM Response Incomplete
**Symptom:** `extracted_fields` empty or missing fields  
**Problem:** Prompt not clear or LLM guessing  
**Solution:** Improve prompt or set defaults:
```python
extracted_fields = parsed.get("extracted_fields", {})
# Fill in defaults for missing fields
if "vendor" not in extracted_fields:
    extracted_fields["vendor"] = "Unknown"
```

### Pitfall 4: Rate Limiting
**Symptom:** "Rate limit exceeded" from LLM API  
**Problem:** Too many requests too fast  
**Solution:** Add retry logic:
```python
import asyncio

async def call_with_retry(self, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await self.llm_router.call(system_prompt, prompt)
        except RateLimitError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

## Inputs You Depend On

- ✅ `IngestedDocument` from Domain 1 (Person A)
- ✅ LLM API keys in `.env`
- ✅ `shared/types.py` (provided, LOCKED)
- ✅ `shared/fixtures.py` with sample documents (provided)
- ✅ `prompts.py` (provided)

## Outputs You Provide

- `ClassificationResult` with:
  - ✅ Valid `doc_type` (one of 7 types)
  - ✅ **Confidence 0.0-1.0** (most important!)
  - ✅ Clear `reasoning`
  - ✅ Extracted fields (vendor, amount, date, etc.)
  - ✅ Suggested reviewer

Domain 3 depends on your confidence and doc_type being correct. Wrong classification = file in wrong folder.

## Success Checklist

- [ ] LLM router working (Cerebras, Groq, or Gemini)
- [ ] Classification returning valid ClassificationResult
- [ ] Confidence scores always 0.0-1.0
- [ ] Doc_type always one of 7 valid types
- [ ] Extracted fields populated (vendor, amount, date, etc.)
- [ ] Required reviewer correctly mapped
- [ ] domain_2_classifier tests passing: `pytest domain_2_classifier/ -v`
- [ ] No cross-domain imports
- [ ] Ready to pass to Domain 3

## What's Next (Not Your Job)

- Domain 3 will take your ClassificationResult and move files to Box
- You don't need to worry about Box integration or notifications

Just make sure your classifications are accurate and your output is complete.

---

## Quick Reference

**Your workflow:**
1. `llm_router.py` - Switch between LLM providers
2. `service.py` - Call LLM and parse response
3. `tests/` - Unit tests for classification
4. `schemas.py` & `prompts.py` - Already complete, use them

**Key files (read-only):**
- `backend/shared/types.py` - Your output schema (LOCKED)
- `prompts.py` - System and user prompts (optimized)
- `fixtures.py` - Sample test documents

**Your contract:**
- **Input:** `IngestedDocument` with full text content
- **Output:** `ClassificationResult` with doc_type, confidence, fields
- **Success Metric:** Domain 3 can route documents correctly

---

Good luck! You're the AI brain of this system. Get it right and everything else falls into place. 🧠
