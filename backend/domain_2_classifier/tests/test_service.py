"""Tests for Domain 2 classification service."""

import pytest
from backend.shared.fixtures import (
    MOCK_INGESTED_DOCUMENT_INVOICE,
    MOCK_INGESTED_DOCUMENT_CONTRACT,
    MOCK_CLASSIFICATION_INVOICE,
)
from backend.domain_2_classifier.service import ClassificationService


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
        raise NotImplementedError("TODO: Implement invoice classification test")

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
        raise NotImplementedError("TODO: Implement contract classification test")

    @pytest.mark.asyncio
    async def test_classify_confidence_score(self, service):
        """
        TODO: Test confidence score validation.

        1. Classify document
        2. Assert confidence is float between 0.0 and 1.0
        3. Assert confidence is reasonable (not 0.0 or 1.0 unless justified)
        """
        raise NotImplementedError("TODO: Implement confidence score test")

    def test_validate_confidence_valid(self, service):
        """
        TODO: Test confidence validation with valid score.

        1. Call service._validate_confidence(0.95)
        2. Assert returns True
        """
        raise NotImplementedError("TODO: Implement valid confidence test")

    def test_validate_confidence_invalid(self, service):
        """
        TODO: Test confidence validation with invalid score.

        1. Call service._validate_confidence(1.5)
        2. Assert raises ConfidenceScoreError
        """
        raise NotImplementedError("TODO: Implement invalid confidence test")

    def test_parse_llm_response_valid(self, service):
        """
        TODO: Test parsing valid LLM response.

        1. Create mock JSON response from LLM
        2. Call service._parse_llm_response()
        3. Assert returns parsed dict with all fields
        """
        raise NotImplementedError("TODO: Implement valid LLM response parsing test")

    def test_parse_llm_response_invalid(self, service):
        """
        TODO: Test parsing invalid LLM response.

        1. Create malformed JSON response
        2. Call service._parse_llm_response()
        3. Assert raises InvalidClassificationResultError
        """
        raise NotImplementedError("TODO: Implement invalid LLM response parsing test")
