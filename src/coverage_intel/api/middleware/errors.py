"""Global error handling middleware & response envelopes."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ...errors import CoverageIntelError


def error_response(exc: CoverageIntelError) -> JSONResponse:
    """Build the typed error envelope. Never includes a partial answer."""
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": exc.error_code,
            "message": str(exc),
            "retryable": exc.retryable,
        },
    )


def setup_error_handlers(app: FastAPI) -> None:
    """Register typed domain exception handlers on the application."""

    @app.exception_handler(CoverageIntelError)
    async def _handle_known_error(_request: Request, exc: CoverageIntelError) -> JSONResponse:
        return error_response(exc)

