"""Document orchestration - chains Domain 2 and Domain 3 automatically."""

from .orchestrator import DocumentOrchestrator, get_orchestrator
from .routes import router

__all__ = ["DocumentOrchestrator", "get_orchestrator", "router"]
