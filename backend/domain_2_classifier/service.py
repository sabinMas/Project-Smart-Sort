"""Business logic for Domain 2: AI Classification."""

import json
from backend.shared.types import IngestedDocument, ClassificationResult
from backend.shared.logging import get_logger
from backend.shared.config import REVIEWER_MAPPING, Config
from backend.domain_2_classifier.llm_router import LLMRouter
from backend.domain_2_classifier.prompts import CLASSIFICATION_SYSTEM_PROMPT, get_classification_prompt

logger = get_logger(__name__)


class ClassificationService:
    """Service for AI-powered document classification."""

    def __init__(self):
        """Initialize classification service with LLM router."""
        self.llm_router = LLMRouter()

    async def classify(self, document: IngestedDocument) -> ClassificationResult:
        """
        Classify an ingested document using LLM.

        TODO: Implement classification logic:
        1. Get document text from IngestedDocument.content
        2. Call self.llm_router.call() with system and user prompts
        3. Parse JSON response from LLM
        4. Validate confidence is 0.0-1.0
        5. Map doc_type to required_reviewer using REVIEWER_MAPPING
        6. Create ClassificationResult with all fields
        7. Log classification result
        8. Return ClassificationResult

        Args:
            document: IngestedDocument to classify

        Returns:
            ClassificationResult: Classification with doc_type, confidence, fields

        Raises:
            ClassificationError: If LLM call or parsing fails
            InvalidClassificationResultError: If result is malformed
        """
        raise NotImplementedError("TODO: Implement LLM-based classification")

    def _parse_llm_response(self, response: str) -> dict:
        """
        Parse and validate LLM JSON response.

        TODO: Implement parsing:
        1. Extract JSON from response text
        2. Validate required fields present:
           - doc_type (one of valid types)
           - confidence (0.0-1.0)
           - reasoning (non-empty string)
           - extracted_fields (dict)
           - required_reviewer (optional)
           - metadata_tags (list)
        3. Return parsed dict

        Args:
            response: Raw text response from LLM

        Returns:
            dict: Parsed classification data

        Raises:
            InvalidClassificationResultError: If JSON is invalid or missing fields
        """
        raise NotImplementedError("TODO: Implement LLM response parsing")

    def _validate_confidence(self, confidence: float) -> bool:
        """
        Validate confidence score is in valid range.

        Args:
            confidence: Confidence value to validate

        Returns:
            bool: True if valid

        Raises:
            ConfidenceScoreError: If confidence is outside [0.0, 1.0]
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {confidence}")
        return True
