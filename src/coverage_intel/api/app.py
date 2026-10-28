"""FastAPI Application Factory & Architecture Configuration.

Phase: phase-07-backend-api.md
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from ..config import get_settings
from ..logging_config import configure_logging
from ..services.indexing_service import ensure_corpus_indexed
from .middleware.errors import error_response as _error_response, setup_error_handlers
from .middleware.request_tracing import RequestTracingMiddleware
from .routers import coverage_router, documents_router, health_router, system_router, mount_ui

logger = logging.getLogger("coverage-intel.app")

DESCRIPTION = """
**Coverage Intel** — RAG-based insurance coverage intelligence assistant.

Decision support for claims adjusters. This system does **not** approve or deny
claims, calculate settlements, or replace human, legal, compliance, or
underwriting judgment.
"""


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    yield


def create_app() -> FastAPI:
    """Build the production-ready FastAPI application with modular layers."""
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format == "json")

    app = FastAPI(
        title="Coverage Intel",
        description=DESCRIPTION,
        version="0.1.0",
        lifespan=lifespan,
    )

    # 1. Register ASGI Middlewares
    app.add_middleware(RequestTracingMiddleware)

    # 2. Register Global Exception Handlers
    setup_error_handlers(app)

    # 3. Include Modular Routers
    app.include_router(coverage_router)
    app.include_router(documents_router)
    app.include_router(health_router)
    app.include_router(system_router)

    # 4. Mount Static UI and Root Navigation
    mount_ui(app)

    return app


# Singleton ASGI application instance
app = create_app()
