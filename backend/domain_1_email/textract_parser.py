"""Amazon Textract integration for document extraction."""

import base64
import json
from typing import Optional
from backend.shared.config import Config
from backend.shared.logging import get_logger

logger = get_logger(__name__)


class TextractParser:
    """Extracts text from PDFs and documents using Amazon Textract."""

    def __init__(self):
        """Initialize Textract client."""
        self.enabled = Config.USE_TEXTRACT
        self.client = None

        if self.enabled:
            try:
                import boto3
                self.client = boto3.client(
                    'textract',
                    region_name=Config.AWS_REGION,
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                )
                logger.info(f"Textract initialized for region: {Config.AWS_REGION}")
            except Exception as e:
                logger.warning(f"Failed to initialize Textract: {e}. Falling back to basic extraction.")
                self.enabled = False

    async def extract_pdf_text(self, pdf_bytes: bytes, filename: str = "document.pdf") -> str:
        """
        Extract text from PDF using Textract.

        Args:
            pdf_bytes: Raw PDF file bytes
            filename: Original filename (for logging)

        Returns:
            str: Extracted text from document
        """
        if not self.enabled or not self.client:
            logger.info(f"Textract not available, returning empty text for {filename}")
            return ""

        try:
            logger.info(f"Extracting text from {filename} using Textract...")

            # Call Textract to detect document text
            response = self.client.detect_document_text(
                Document={'Bytes': pdf_bytes}
            )

            # Extract text from response
            text_lines = []
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    text = block.get('Text', '').strip()
                    if text:
                        text_lines.append(text)

            extracted_text = '\n'.join(text_lines)
            logger.info(
                f"Successfully extracted {len(extracted_text)} chars from {filename} "
                f"({len(text_lines)} lines)"
            )
            return extracted_text

        except Exception as e:
            logger.error(f"Textract extraction failed for {filename}: {e}")
            return ""

    async def extract_from_attachment(self, attachment: dict) -> str:
        """
        Extract text from email attachment.

        Args:
            attachment: Dict with 'filename' and 'content' (base64 encoded)

        Returns:
            str: Extracted text from attachment
        """
        try:
            filename = attachment.get('filename', 'attachment')
            content_base64 = attachment.get('content', '')
            content_type = attachment.get('content_type', 'application/octet-stream')

            # Decode base64 content
            try:
                pdf_bytes = base64.b64decode(content_base64)
            except Exception as e:
                logger.error(f"Failed to decode attachment {filename}: {e}")
                return ""

            # Only process PDFs
            if 'pdf' not in content_type.lower():
                logger.info(f"Skipping non-PDF attachment: {filename} ({content_type})")
                return ""

            return await self.extract_pdf_text(pdf_bytes, filename)

        except Exception as e:
            logger.error(f"Error processing attachment: {e}")
            return ""

    async def extract_table_data(self, pdf_bytes: bytes) -> list:
        """
        Extract tabular data from PDF.

        Args:
            pdf_bytes: Raw PDF file bytes

        Returns:
            list: List of tables found in document (dicts with row/column structure)
        """
        if not self.enabled or not self.client:
            return []

        try:
            response = self.client.analyze_document(
                Document={'Bytes': pdf_bytes},
                FeatureTypes=['TABLES']
            )

            tables = []
            current_table = None
            current_row = []

            for block in response.get('Blocks', []):
                if block['BlockType'] == 'TABLE':
                    if current_table is not None:
                        tables.append(current_table)
                    current_table = {'rows': []}

                elif block['BlockType'] == 'TABLE_ROW' and current_table is not None:
                    if current_row:
                        current_table['rows'].append(current_row)
                    current_row = []

                elif block['BlockType'] == 'TABLE_CELL':
                    text = block.get('Text', '')
                    current_row.append(text)

            # Add last table
            if current_table is not None and current_row:
                current_table['rows'].append(current_row)
                tables.append(current_table)

            logger.info(f"Extracted {len(tables)} tables from document")
            return tables

        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            return []


# Singleton instance
_textract_parser: Optional[TextractParser] = None


def get_textract_parser() -> TextractParser:
    """Get or create Textract parser singleton."""
    global _textract_parser
    if _textract_parser is None:
        _textract_parser = TextractParser()
    return _textract_parser
