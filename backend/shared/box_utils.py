"""Utilities for Box integration."""

from enum import Enum
from typing import Optional
from .config import Config


class BoxFolder(str, Enum):
    """Box folder names in the processing workflow."""

    INBOX = "inbox"
    NEEDS_REVIEW = "needs_review"
    NEEDS_SIGNATURE = "needs_signature"
    PENDING_RETURN = "pending_return"
    ARCHIVE = "archive"


def get_folder_id(folder: BoxFolder) -> str:
    """Get Box folder ID from folder enum."""
    folder_map = {
        BoxFolder.INBOX: Config.BOX_INBOX_FOLDER_ID,
        BoxFolder.NEEDS_REVIEW: Config.BOX_NEEDS_REVIEW_FOLDER_ID,
        BoxFolder.NEEDS_SIGNATURE: Config.BOX_NEEDS_SIGNATURE_FOLDER_ID,
        BoxFolder.PENDING_RETURN: Config.BOX_PENDING_RETURN_FOLDER_ID,
        BoxFolder.ARCHIVE: Config.BOX_ARCHIVE_FOLDER_ID,
    }
    folder_id = folder_map.get(folder)
    if not folder_id:
        raise ValueError(f"Folder {folder} not configured")
    return folder_id


def get_folder_path(folder: BoxFolder) -> str:
    """Get logical path for a folder."""
    folder_map = {
        BoxFolder.INBOX: "/Incoming Documents",
        BoxFolder.NEEDS_REVIEW: "/PROCESSING/Needs Review",
        BoxFolder.NEEDS_SIGNATURE: "/PROCESSING/Needs Signature",
        BoxFolder.PENDING_RETURN: "/PROCESSING/Pending Return",
        BoxFolder.ARCHIVE: "/ARCHIVE",
    }
    return folder_map.get(folder, "")


def get_metadata_filename(document_id: str, metadata_type: str) -> str:
    """Generate metadata filename for Box."""
    return f"{document_id}.{metadata_type}.json"


def parse_document_id_from_filename(filename: str) -> Optional[str]:
    """Extract document ID from metadata filename."""
    if ".metadata.json" in filename:
        return filename.replace(".metadata.json", "")
    if ".recipients.json" in filename:
        return filename.replace(".recipients.json", "")
    if ".state.json" in filename:
        return filename.replace(".state.json", "")
    return None
