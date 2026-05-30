"""Box SDK wrapper for Domain 3: Box Integration."""

from typing import Optional, Dict, Any
from backend.shared.config import Config
from backend.shared.logging import get_logger

logger = get_logger(__name__)


class BoxClient:
    """Wrapper around box-sdk-gen for simplified Box API interactions."""

    def __init__(self):
        """
        TODO: Initialize Box API client.

        1. Use BOX_CLIENT_ID and BOX_CLIENT_SECRET from config
        2. Handle JWT authentication or OAuth flow
        3. Initialize box-sdk-gen client
        4. Test connection with enterprise ID
        5. Raise BoxAuthenticationError if auth fails
        """
        self.client = None
        raise NotImplementedError("TODO: Implement Box client initialization")

    async def upload_file(
        self,
        file_path: str,
        folder_id: str,
        file_name: str,
    ) -> str:
        """
        Upload a file to Box.

        TODO: Implement file upload:
        1. Read file from path
        2. Upload to folder_id with file_name
        3. Return Box file ID

        Args:
            file_path: Local file path to upload
            folder_id: Destination Box folder ID
            file_name: Name for file in Box

        Returns:
            str: Box file ID of uploaded file

        Raises:
            BoxUploadError: If upload fails
        """
        raise NotImplementedError("TODO: Implement file upload")

    async def move_file(
        self,
        file_id: str,
        destination_folder_id: str,
    ) -> str:
        """
        Move a file to a different Box folder.

        TODO: Implement file move:
        1. Move file_id to destination folder
        2. Return updated file ID

        Args:
            file_id: Box file ID to move
            destination_folder_id: Destination folder ID

        Returns:
            str: Updated file ID

        Raises:
            BoxFileNotFoundError: If file not found
        """
        raise NotImplementedError("TODO: Implement file move")

    async def get_or_create_folder(self, folder_path: str, parent_id: str = None) -> str:
        """
        Get or create a folder at the given path.

        TODO: Implement folder creation:
        1. Parse folder_path (e.g., "/Invoices/2024/May")
        2. Create intermediate folders if needed
        3. Return final folder ID

        Args:
            folder_path: Path like "/Invoices/2024/May"
            parent_id: Parent folder ID (if None, use root)

        Returns:
            str: Folder ID for the destination

        Raises:
            BoxIntegrationError: If folder creation fails
        """
        raise NotImplementedError("TODO: Implement folder creation")

    async def list_files(self, folder_id: str) -> list:
        """
        List files in a Box folder.

        Args:
            folder_id: Box folder ID

        Returns:
            list: List of file metadata dicts
        """
        raise NotImplementedError("TODO: Implement list files")
