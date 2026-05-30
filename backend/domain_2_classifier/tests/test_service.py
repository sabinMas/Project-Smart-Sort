"""Tests for Domain 2 classification service."""

import pytest
import json
from unittest.mock import AsyncMock, patch
from backend.shared.fixtures import (
    MOCK_INGESTED_DOCUMENT_INVOICE,
    MOCK_INGESTED_DOCUMENT_CONTRACT,
    MOCK_CLASSIFICATION_INVOICE,
)
from backend.domain_2_classifier.service import ClassificationService
from backend.shared.errors import (
    ConfidenceScoreError,
    InvalidClassificationResultError,
    ClassificationError,
)


@pytest.mark.domain2
class TestClassificationService:
    """Tests for ClassificationService."""

    @pytest.fixture
    def service(self):
        """Create classification service instance."""
        return ClassificationService()

    @pytest.mark.asyncio
    async def test_classify_invoice(self, service):
        """
        TODO: Test classifying an invoice document.

        1. Use MOCK_INGESTED_DOCUMENT_INVOICE fixture
        2. Call service.classify()
        3. Assert returned ClassificationResult
        4. Assert doc_type == "invoice"
        5. Assert confidence >= 0.85
        6. Assert extracted_fields contains vendor, amount, date
        7. Assert required_reviewer == "finance"
        """
        # Mock LLM response for invoice
        mock_llm_response = json.dumps({
            "doc_type": "invoice",
            "confidence": 0.98,
            "reasoning": "Document contains invoice header, itemized services, and payment terms typical of business invoices.",
            "extracted_fields": {
                "vendor": "ACME Corporation",
                "amount": 5000.00,
                "date": "2024-05-15",
            },
            "required_reviewer": "finance",
            "metadata_tags": ["vendor:acme", "amount:5000", "q2_2024"],
        })

        with patch.object(service.llm_router, "call", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_llm_response

            result = await service.classify(MOCK_INGESTED_DOCUMENT_INVOICE)

            # Assert returned ClassificationResult
            assert result is not None
            assert result.document_id == MOCK_INGESTED_DOCUMENT_INVOICE.id
            # Assert doc_type == "invoice"
            assert result.doc_type == "invoice"
            # Assert confidence >= 0.85
            assert result.confidence >= 0.85
            assert result.confidence == 0.98
            # Assert extracted_fields contains vendor, amount, date
            assert "vendor" in result.extracted_fields
            assert "amount" in result.extracted_fields
            assert "date" in result.extracted_fields
            # Assert required_reviewer == "finance"
            assert result.required_reviewer == "finance"

    @pytest.mark.asyncio
    async def test_classify_contract(self, service):
        """
        TODO: Test classifying a contract document.

        1. Use MOCK_INGESTED_DOCUMENT_CONTRACT fixture
        2. Call service.classify()
        3. Assert doc_type == "contract"
        4. Assert confidence >= 0.85
        5. Assert required_reviewer == "legal"
        """
        mock_llm_response = json.dumps({
            "doc_type": "contract",
            "confidence": 0.95,
            "reasoning": "Document contains service agreement with parties, terms, conditions, and signature blocks typical of legal contracts.",
            "extracted_fields": {
                "contract_type": "Service Agreement",
                "parties": ["ABC Services Inc.", "Your Organization"],
                "contract_value": 50000.00,
            },
            "required_reviewer": "legal",
            "metadata_tags": ["contract", "services", "legal"],
        })

        with patch.object(service.llm_router, "call", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_llm_response

            result = await service.classify(MOCK_INGESTED_DOCUMENT_CONTRACT)

            # Assert doc_type == "contract"
            assert result.doc_type == "contract"
            # Assert confidence >= 0.85
            assert result.confidence >= 0.85
            assert result.confidence == 0.95
            # Assert required_reviewer == "legal"
            assert result.required_reviewer == "legal"

    @pytest.mark.asyncio
    async def test_classify_confidence_score(self, service):
        """
        TODO: Test confidence score validation.

        1. Classify document
        2. Assert confidence is float between 0.0 and 1.0
        3. Assert confidence is reasonable (not 0.0 or 1.0 unless justified)
        """
        mock_llm_response = json.dumps({
            "doc_type": "invoice",
            "confidence": 0.87,
            "reasoning": "High confidence classification.",
            "extracted_fields": {"vendor": "Test Corp"},
            "required_reviewer": "finance",
            "metadata_tags": ["test"],
        })

        with patch.object(service.llm_router, "call", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_llm_response

            result = await service.classify(MOCK_INGESTED_DOCUMENT_INVOICE)

            # Assert confidence is float between 0.0 and 1.0
            assert isinstance(result.confidence, float)
            assert 0.0 <= result.confidence <= 1.0
            # Assert confidence is reasonable
            assert 0.0 < result.confidence < 1.0

    def test_validate_confidence_valid(self, service):
        """
        TODO: Test confidence validation with valid score.

        1. Call service._validate_confidence(0.95)
        2. Assert returns True
        """
        assert service._validate_confidence(0.95) is True
        assert service._validate_confidence(0.0) is True
        assert service._validate_confidence(1.0) is True
        assert service._validate_confidence(0.5) is True

    def test_validate_confidence_invalid(self, service):
        """
        TODO: Test confidence validation with invalid score.

        1. Call service._validate_confidence(1.5)
        2. Assert raises ConfidenceScoreError
        """
        with pytest.raises(ConfidenceScoreError):
            service._validate_confidence(1.5)

        with pytest.raises(ConfidenceScoreError):
            service._validate_confidence(-0.1)

        with pytest.raises(ConfidenceScoreError):
            service._validate_confidence(2.0)

    def test_parse_llm_response_valid(self, service):
        """
        TODO: Test parsing valid LLM response.

        1. Create mock JSON response from LLM
        2. Call service._parse_llm_response()
        3. Assert returns parsed dict with all fields
        """
        valid_response = json.dumps({
            "doc_type": "invoice",
            "confidence": 0.98,
            "reasoning": "This is a valid invoice.",
            "extracted_fields": {"vendor": "ACME", "amount": 1000},
            "required_reviewer": "finance",
            "metadata_tags": ["invoice", "vendor:acme"],
        })

        result = service._parse_llm_response(valid_response)

        # Assert returns parsed dict with all fields
        assert result["doc_type"] == "invoice"
        assert result["confidence"] == 0.98
        assert result["reasoning"] == "This is a valid invoice."
        assert result["extracted_fields"] == {"vendor": "ACME", "amount": 1000}
        assert result["required_reviewer"] == "finance"
        assert result["metadata_tags"] == ["invoice", "vendor:acme"]

    def test_parse_llm_response_with_markdown_json(self, service):
        """Test parsing LLM response with JSON in markdown code block."""
        response_with_markdown = """Here's the classification:

```json
{
  "doc_type": "contract",
  "confidence": 0.95,
  "reasoning": "Legal document",
  "extracted_fields": {"parties": ["A", "B"]},
  "required_reviewer": "legal",
  "metadata_tags": ["contract"]
}
```

That's the result."""

        result = service._parse_llm_response(response_with_markdown)

        assert result["doc_type"] == "contract"
        assert result["confidence"] == 0.95

    def test_parse_llm_response_invalid_json(self, service):
        """
        TODO: Test parsing invalid LLM response.

        1. Create malformed JSON response
        2. Call service._parse_llm_response()
        3. Assert raises InvalidClassificationResultError
        """
        invalid_response = "This is not valid JSON at all"

        with pytest.raises(InvalidClassificationResultError):
            service._parse_llm_response(invalid_response)

    def test_parse_llm_response_missing_fields(self, service):
        """Test parsing response with missing required fields."""
        incomplete_response = json.dumps({
            "doc_type": "invoice",
            "confidence": 0.95,
            # Missing reasoning, extracted_fields, metadata_tags
        })

        with pytest.raises(InvalidClassificationResultError) as exc_info:
            service._parse_llm_response(incomplete_response)

        assert "Missing required fields" in str(exc_info.value)

    def test_parse_llm_response_invalid_doc_type(self, service):
        """Test parsing response with invalid doc_type."""
        invalid_response = json.dumps({
            "doc_type": "invalid_type",
            "confidence": 0.95,
            "reasoning": "Test",
            "extracted_fields": {},
            "metadata_tags": [],
        })

        with pytest.raises(InvalidClassificationResultError) as exc_info:
            service._parse_llm_response(invalid_response)

        assert "Invalid doc_type" in str(exc_info.value)

    def test_parse_llm_response_invalid_confidence(self, service):
        """Test parsing response with invalid confidence value."""
        invalid_confidence = json.dumps({
            "doc_type": "invoice",
            "confidence": 1.5,
            "reasoning": "Test",
            "extracted_fields": {},
            "metadata_tags": [],
        })

        with pytest.raises(InvalidClassificationResultError) as exc_info:
            service._parse_llm_response(invalid_confidence)

        assert "Confidence must be between 0.0 and 1.0" in str(exc_info.value)

    def test_parse_llm_response_empty_reasoning(self, service):
        """Test parsing response with empty reasoning."""
        invalid_response = json.dumps({
            "doc_type": "invoice",
            "confidence": 0.95,
            "reasoning": "   ",
            "extracted_fields": {},
            "metadata_tags": [],
        })

        with pytest.raises(InvalidClassificationResultError) as exc_info:
            service._parse_llm_response(invalid_response)

        assert "non-empty string" in str(exc_info.value)
