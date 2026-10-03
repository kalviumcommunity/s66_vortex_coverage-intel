"""FastAPI application factory.

Phase: phase-07-backend-api.md
"""

from __future__ import annotations

from fastapi import FastAPI

from ..config import get_settings
from ..errors import CoverageIntelError
from ..logging_config import configure_logging

DESCRIPTION = """
**Coverage Intel** — RAG-based insurance coverage intelligence assistant.

Decision support for claims adjusters. This system does **not** approve or deny
claims, calculate settlements, or replace human, legal, compliance, or
underwriting judgment.
"""


def create_app() -> FastAPI:
    """Build the FastAPI application with typed error handling."""
    configure_logging(get_settings().log_level, get_settings().log_format == "json")

    app = FastAPI(
        title="Coverage Intel",
        description=DESCRIPTION,
        version="0.1.0",
    )

    @app.exception_handler(CoverageIntelError)
    async def _handle_known_error(_request, exc: CoverageIntelError):
        return _error_response(exc)

    return app


def _error_response(exc: CoverageIntelError) -> Any:
    """Build the error envelope. Never includes a partial answer."""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": exc.error_code,
            "message": str(exc),
            "retryable": exc.retryable,
        },
    )


app = create_app()
