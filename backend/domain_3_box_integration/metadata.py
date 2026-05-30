"""Metadata management for Domain 3: Box Integration."""

from typing import Dict, Any, Optional
from backend.shared.types import ClassificationResult
from backend.shared.errors import MetadataApplicationError
from backend.shared.logging import get_logger

logger = get_logger(__name__)


class MetadataManager:
    """Manages metadata template application to Box files."""

    def __init__(self, box_client: Optional[Any] = None):
        """Initialize metadata manager with optional Box client.

        Args:
            box_client: BoxClient instance for applying metadata
        """
        self.box_client = box_client

    async def apply_metadata(
        self,
        file_id: str,
        metadata: Dict[str, Any],
        template_name: str = "box_smart_inbox_metadata",
    ) -> bool:
        """Apply metadata template to a Box file.

        Validates metadata, then delegates to the BoxClient for actual
        API interaction. This layer handles validation and error wrapping.

        Args:
            file_id: Box file ID
            metadata: Dict of metadata key-value pairs
            template_name: Metadata template name in Box

        Returns:
            bool: True if successful

        Raises:
            MetadataApplicationError: If application fails
        """
        try:
            self._validate_metadata(metadata)
        except ValueError as e:
            raise MetadataApplicationError(f"Invalid metadata: {e}")

        # Actually apply metadata if BoxClient is available
        if self.box_client:
            try:
                await self.box_client.apply_metadata(file_id, metadata)
                logger.info(
                    f"Metadata applied for file {file_id}, "
                    f"template={template_name}, fields={list(metadata.keys())}"
                )
            except Exception as e:
                raise MetadataApplicationError(f"Failed to apply metadata: {e}")
        else:
            logger.info(
                f"Metadata validated for file {file_id}, "
                f"template={template_name}, fields={list(metadata.keys())} "
                f"(no BoxClient available)"
            )

        return True

    def _validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate metadata against schema.

        Args:
            metadata: Metadata dict to validate

        Returns:
            bool: True if valid

        Raises:
            ValueError: If metadata is invalid
        """
        required_fields = ["document_type", "confidence"]
        for field_name in required_fields:
            if field_name not in metadata:
                raise ValueError(f"Missing required metadata field: {field_name}")

        # Validate confidence is a string representation of a float
        try:
            confidence_val = float(metadata["confidence"])
            if not 0.0 <= confidence_val <= 1.0:
                raise ValueError(
                    f"Confidence must be between 0.0 and 1.0, got {confidence_val}"
                )
        except (ValueError, TypeError) as e:
            if "Confidence must be" in str(e):
                raise
            raise ValueError(f"Invalid confidence value: {metadata['confidence']}")

        return True

    def build_metadata_dict(self, classification_result: ClassificationResult) -> Dict[str, Any]:
        """Build metadata dictionary from classification result.

        Args:
            classification_result: ClassificationResult from Domain 2

        Returns:
            Dict: Metadata ready to apply to Box file
        """
        return {
            "document_type": classification_result.doc_type,
            "confidence": str(classification_result.confidence),
            "extracted_vendor": classification_result.extracted_fields.get("vendor", ""),
            "extracted_amount": str(
                classification_result.extracted_fields.get("amount", "")
            ),
            "tags": ", ".join(classification_result.metadata_tags),
        }
