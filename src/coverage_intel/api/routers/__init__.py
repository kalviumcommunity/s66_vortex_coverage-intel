"""API Routers package."""

from .coverage import router as coverage_router
from .documents import router as documents_router
from .health import router as health_router
from .system import router as system_router
from .ui import mount_ui

__all__ = ["coverage_router", "documents_router", "health_router", "system_router", "mount_ui"]
