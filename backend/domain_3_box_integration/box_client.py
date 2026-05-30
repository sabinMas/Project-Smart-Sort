"""Box SDK wrapper for Domain 3: Box Integration."""

import asyncio
from typing import Optional, Dict, Any, List
from backend.shared.config import Config
from backend.shared.errors import (
    BoxAuthenticationError,
    BoxIntegrationError,
    BoxFileNotFoundError,
    BoxUploadError,
)
from backend.shared.logging import get_logger

logger = get_logger(__name__)


class BoxClient:
    """Wrapper around box-sdk-gen for simplified Box API interactions.

    Supports two modes:
    - Demo mode (Config.DEMO_MODE=True): Returns simulated responses for testing/demo
    - Live mode: Uses box-sdk-gen to interact with real Box API
    """

    def __init__(self):
        """Initialize Box API client.

        In demo mode, skips real authentication and uses simulated responses.
        In live mode, authenticates with Box using client credentials.
        """
        self.client = None
        self._demo_mode = Config.DEMO_MODE
        self._demo_folder_counter = 1000
        self._demo_file_counter = 5000
        self._demo_folders: Dict[str, str] = {}  # path -> folder_id

        if self._demo_mode:
            logger.info("BoxClient initialized in DEMO mode")
            return

        # Live mode: initialize real Box SDK client
        try:
            from box_sdk_gen import BoxClient as SdkBoxClient
            from box_sdk_gen.managers.authorization import AuthorizeUser
            from box_sdk_gen import BoxCCGAuth, CCGConfig

            ccg_config = CCGConfig(
                client_id=Config.BOX_CLIENT_ID,
                client_secret=Config.BOX_CLIENT_SECRET,
                enterprise_id=Config.BOX_ENTERPRISE_ID,
            )
            auth = BoxCCGAuth(config=ccg_config)
            self.client = SdkBoxClient(auth=auth)
            logger.info("BoxClient initialized with CCG authentication")
        except ImportError:
            logger.warning("box-sdk-gen not available, falling back to demo mode")
            self._demo_mode = True
        except Exception as e:
            raise BoxAuthenticationError(f"Failed to authenticate with Box: {e}")

    async def upload_file(
        self,
        file_path: str,
        folder_id: str,
        file_name: str,
    ) -> str:
        """Upload a file to Box.

        Args:
            file_path: Local file path to upload
            folder_id: Destination Box folder ID
            file_name: Name for file in Box

        Returns:
            str: Box file ID of uploaded file

        Raises:
            BoxUploadError: If upload fails
        """
        if self._demo_mode:
            self._demo_file_counter += 1
            file_id = f"file_{self._demo_file_counter}"
            logger.info(
                f"[DEMO] Uploaded '{file_name}' to folder {folder_id} -> {file_id}"
            )
            return file_id

        try:
            import io

            with open(file_path, "rb") as f:
                file_content = f.read()

            # Use asyncio.to_thread to run synchronous Box SDK call without blocking
            uploaded_file = await asyncio.to_thread(
                self.client.uploads.upload_file,
                attributes={
                    "name": file_name,
                    "parent": {"id": folder_id},
                },
                file=io.BytesIO(file_content),
            )
            file_id = uploaded_file.entries[0].id
            logger.info(f"Uploaded '{file_name}' to folder {folder_id} -> {file_id}")
            return file_id
        except Exception as e:
            raise BoxUploadError(f"Failed to upload file '{file_name}': {e}")

    async def move_file(
        self,
        file_id: str,
        destination_folder_id: str,
    ) -> str:
        """Move a file to a different Box folder.

        Args:
            file_id: Box file ID to move
            destination_folder_id: Destination folder ID

        Returns:
            str: Updated file ID

        Raises:
            BoxFileNotFoundError: If file not found
        """
        if self._demo_mode:
            logger.info(
                f"[DEMO] Moved file {file_id} to folder {destination_folder_id}"
            )
            return file_id

        try:
            updated_file = await asyncio.to_thread(
                self.client.files.update_file_by_id,
                file_id=file_id,
                parent={"id": destination_folder_id},
            )
            logger.info(f"Moved file {file_id} to folder {destination_folder_id}")
            return updated_file.id
        except Exception as e:
            raise BoxFileNotFoundError(
                f"Failed to move file {file_id}: {e}"
            )

    async def get_or_create_folder(
        self, folder_path: str, parent_id: Optional[str] = None
    ) -> str:
        """Get or create a folder at the given path.

        Parses folder_path (e.g., "/Invoices/2024/May") and creates
        intermediate folders as needed.

        Args:
            folder_path: Path like "/Invoices/2024/May"
            parent_id: Parent folder ID (if None, use root "0")

        Returns:
            str: Folder ID for the destination

        Raises:
            BoxIntegrationError: If folder creation fails
        """
        if self._demo_mode:
            # Check cache first
            if folder_path in self._demo_folders:
                return self._demo_folders[folder_path]

            self._demo_folder_counter += 1
            folder_id = f"folder_{self._demo_folder_counter}"
            self._demo_folders[folder_path] = folder_id
            logger.info(f"[DEMO] Created folder '{folder_path}' -> {folder_id}")
            return folder_id

        # Live mode: traverse/create path
        parent_id = parent_id or Config.BOX_DEMO_FOLDER_ID or "0"
        parts = [p for p in folder_path.split("/") if p]

        current_parent_id = parent_id
        current_path = ""

        for part in parts:
            current_path += f"/{part}"

            # Check cache
            if current_path in self._demo_folders:
                current_parent_id = self._demo_folders[current_path]
                continue

            try:
                # Try to find existing folder
                folder_id = await self._find_folder(current_parent_id, part)
                if folder_id:
                    self._demo_folders[current_path] = folder_id
                    current_parent_id = folder_id
                else:
                    # Create it
                    folder_id = await self._create_folder(current_parent_id, part)
                    self._demo_folders[current_path] = folder_id
                    current_parent_id = folder_id
            except Exception as e:
                raise BoxIntegrationError(
                    f"Failed to get/create folder '{current_path}': {e}"
                )

        return current_parent_id

    async def _find_folder(self, parent_id: str, folder_name: str) -> Optional[str]:
        """Find a folder by name within a parent folder.

        Args:
            parent_id: Parent folder ID to search in
            folder_name: Name of folder to find

        Returns:
            Optional[str]: Folder ID if found, None otherwise
        """
        try:
            items = await asyncio.to_thread(
                self.client.folders.get_folder_items,
                folder_id=parent_id,
            )
            for item in items.entries:
                if item.type == "folder" and item.name == folder_name:
                    return item.id
            return None
        except Exception:
            return None

    async def _create_folder(self, parent_id: str, folder_name: str) -> str:
        """Create a new folder.

        Args:
            parent_id: Parent folder ID
            folder_name: Name for new folder

        Returns:
            str: New folder ID
        """
        try:
            folder = await asyncio.to_thread(
                self.client.folders.create_folder,
                name=folder_name,
                parent={"id": parent_id},
            )
            logger.info(f"Created folder '{folder_name}' in {parent_id}")
            return folder.id
        except Exception as e:
            # Folder might already exist (race condition)
            existing = await self._find_folder(parent_id, folder_name)
            if existing:
                return existing
            raise BoxIntegrationError(
                f"Failed to create folder '{folder_name}': {e}"
            )

    async def list_files(self, folder_id: str) -> List[Dict[str, Any]]:
        """List files in a Box folder.

        Args:
            folder_id: Box folder ID

        Returns:
            list: List of file metadata dicts
        """
        if self._demo_mode:
            logger.info(f"[DEMO] Listed files in folder {folder_id}")
            return []

        try:
            items = await asyncio.to_thread(
                self.client.folders.get_folder_items,
                folder_id=folder_id,
            )
            files = []
            for item in items.entries:
                if item.type == "file":
                    files.append({
                        "id": item.id,
                        "name": item.name,
                        "type": item.type,
                    })
            return files
        except Exception as e:
            raise BoxIntegrationError(f"Failed to list files in folder {folder_id}: {e}")

    async def create_task(
        self,
        file_id: str,
        message: str,
        due_at: Optional[str] = None,
    ) -> str:
        """Create a task on a Box file.

        Args:
            file_id: Box file ID
            message: Task description
            due_at: Due date in ISO format (optional)

        Returns:
            str: Task ID
        """
        if self._demo_mode:
            self._demo_file_counter += 1
            task_id = f"task_{self._demo_file_counter}"
            logger.info(f"[DEMO] Created task on file {file_id} -> {task_id}")
            return task_id

        try:
            task_body = {
                "item": {"type": "file", "id": file_id},
                "message": message,
                "action": "review",
            }
            if due_at:
                task_body["due_at"] = due_at

            task = await asyncio.to_thread(
                self.client.tasks.create_task,
                **task_body,
            )
            logger.info(f"Created task on file {file_id} -> {task.id}")
            return task.id
        except Exception as e:
            raise BoxIntegrationError(f"Failed to create task on file {file_id}: {e}")

    async def assign_task_to_user(
        self,
        task_id: str,
        user_email: str,
    ) -> bool:
        """Assign a task to a user by email.

        Args:
            task_id: Box task ID
            user_email: Email of user to assign

        Returns:
            bool: True if successful
        """
        if self._demo_mode:
            logger.info(f"[DEMO] Assigned task {task_id} to {user_email}")
            return True

        try:
            await asyncio.to_thread(
                self.client.tasks.create_task_assignment,
                task_id=task_id,
                assign_to={"login": user_email},
            )
            logger.info(f"Assigned task {task_id} to {user_email}")
            return True
        except Exception as e:
            raise BoxIntegrationError(
                f"Failed to assign task {task_id} to {user_email}: {e}"
            )

    async def apply_metadata(
        self,
        file_id: str,
        metadata: Dict[str, Any],
        template_key: str = "box_smart_inbox_metadata",
        scope: str = "enterprise",
    ) -> bool:
        """Apply metadata to a file.

        Args:
            file_id: Box file ID
            metadata: Key-value metadata to apply
            template_key: Metadata template key
            scope: Metadata scope (enterprise or global)

        Returns:
            bool: True if successful
        """
        if self._demo_mode:
            logger.info(f"[DEMO] Applied metadata to file {file_id}: {metadata}")
            return True

        try:
            await asyncio.to_thread(
                self.client.file_metadata.create_file_metadata_by_id,
                file_id=file_id,
                scope=scope,
                template_key=template_key,
                request_body=metadata,
            )
            logger.info(f"Applied metadata to file {file_id}")
            return True
        except Exception as e:
            # Try updating if already exists
            try:
                updates = [
                    {"op": "replace", "path": f"/{key}", "value": value}
                    for key, value in metadata.items()
                ]
                await asyncio.to_thread(
                    self.client.file_metadata.update_file_metadata_by_id,
                    file_id=file_id,
                    scope=scope,
                    template_key=template_key,
                    request_body=updates,
                )
                logger.info(f"Updated metadata on file {file_id}")
                return True
            except Exception as update_error:
                raise BoxIntegrationError(
                    f"Failed to apply metadata to file {file_id}: {update_error}"
                )
