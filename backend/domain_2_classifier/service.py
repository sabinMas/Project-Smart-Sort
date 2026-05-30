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
        from backend.shared.errors import ClassificationError

        try:
            # 1. Get document text from IngestedDocument.content
            document_text = document.content

            # 2. Call self.llm_router.call() with system and user prompts
            user_prompt = get_classification_prompt(document_text)
            llm_response = await self.llm_router.call(
                CLASSIFICATION_SYSTEM_PROMPT,
                user_prompt
            )
            logger.debug(f"LLM response for document {document.id}: {llm_response[:200]}...")

            # 3. Parse JSON response from LLM
            parsed_result = self._parse_llm_response(llm_response)

            # 4. Validate confidence is 0.0-1.0
            self._validate_confidence(parsed_result["confidence"])

            # 5. Map doc_type to required_reviewer using REVIEWER_MAPPING
            required_reviewer = REVIEWER_MAPPING.get(parsed_result["doc_type"])

            # 6. Create ClassificationResult with all fields
            classification = ClassificationResult(
                document_id=document.id,
                doc_type=parsed_result["doc_type"],
                confidence=parsed_result["confidence"],
                reasoning=parsed_result["reasoning"],
                extracted_fields=parsed_result.get("extracted_fields", {}),
                required_reviewer=required_reviewer,
                metadata_tags=parsed_result.get("metadata_tags", []),
            )

            # 7. Log classification result
            logger.info(
                f"Classified document {document.id} as {classification.doc_type} "
                f"with confidence {classification.confidence}"
            )

            # 8. Return ClassificationResult
            return classification

        except (ValueError, KeyError) as e:
            logger.error(f"Failed to classify document {document.id}: {str(e)}")
            raise ClassificationError(f"Classification failed for document {document.id}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error classifying document {document.id}: {str(e)}")
            raise ClassificationError(f"Unexpected error during classification: {str(e)}")

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
        from backend.shared.errors import InvalidClassificationResultError

        try:
            # 1. Extract JSON from response text
            # First try direct parsing, then look for JSON block in markdown
            parsed = None
            try:
                parsed = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
                if json_match:
                    parsed = json.loads(json_match.group(1))
                else:
                    # Try to find JSON object in response
                    json_match = re.search(r'\{[\s\S]*\}', response)
                    if json_match:
                        parsed = json.loads(json_match.group(0))
                    else:
                        raise InvalidClassificationResultError(
                            "No valid JSON found in LLM response"
                        )

            # 2. Validate required fields present
            required_fields = {
                "doc_type",
                "confidence",
                "reasoning",
                "extracted_fields",
                "metadata_tags",
            }
            missing_fields = required_fields - set(parsed.keys())
            if missing_fields:
                raise InvalidClassificationResultError(
                    f"Missing required fields: {missing_fields}"
                )

            # Validate doc_type is one of valid types
            valid_doc_types = {
                "invoice",
                "contract",
                "resume",
                "receipt",
                "id_document",
                "purchase_order",
                "other",
            }
            if parsed["doc_type"] not in valid_doc_types:
                raise InvalidClassificationResultError(
                    f"Invalid doc_type '{parsed['doc_type']}'. Must be one of: {valid_doc_types}"
                )

            # Validate confidence is number between 0.0 and 1.0
            try:
                confidence = float(parsed["confidence"])
                if not 0.0 <= confidence <= 1.0:
                    raise InvalidClassificationResultError(
                        f"Confidence must be between 0.0 and 1.0, got {confidence}"
                    )
            except (TypeError, ValueError) as e:
                raise InvalidClassificationResultError(
                    f"Confidence must be a number, got {type(parsed['confidence'])}: {e}"
                )

            # Validate reasoning is non-empty string
            if not isinstance(parsed["reasoning"], str) or not parsed["reasoning"].strip():
                raise InvalidClassificationResultError(
                    "Reasoning must be a non-empty string"
                )

            # Validate extracted_fields is dict
            if not isinstance(parsed["extracted_fields"], dict):
                raise InvalidClassificationResultError(
                    f"extracted_fields must be a dict, got {type(parsed['extracted_fields'])}"
                )

            # Validate metadata_tags is list
            if not isinstance(parsed["metadata_tags"], list):
                raise InvalidClassificationResultError(
                    f"metadata_tags must be a list, got {type(parsed['metadata_tags'])}"
                )

            # required_reviewer is optional, but if present should be string or null
            if "required_reviewer" in parsed:
                if parsed["required_reviewer"] is not None and not isinstance(
                    parsed["required_reviewer"], str
                ):
                    raise InvalidClassificationResultError(
                        f"required_reviewer must be string or null, got {type(parsed['required_reviewer'])}"
                    )

            # 3. Return parsed dict
            return {
                "doc_type": parsed["doc_type"],
                "confidence": float(parsed["confidence"]),
                "reasoning": parsed["reasoning"].strip(),
                "extracted_fields": parsed["extracted_fields"],
                "required_reviewer": parsed.get("required_reviewer"),
                "metadata_tags": parsed["metadata_tags"],
            }

        except InvalidClassificationResultError:
            raise
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            raise InvalidClassificationResultError(f"Failed to parse LLM response: {str(e)}")

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
        from backend.shared.errors import ConfidenceScoreError

        if not 0.0 <= confidence <= 1.0:
            raise ConfidenceScoreError(
                f"Confidence must be between 0.0 and 1.0, got {confidence}"
            )
        return True
