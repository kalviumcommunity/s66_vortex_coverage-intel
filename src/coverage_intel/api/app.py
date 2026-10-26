"""FastAPI application factory.

Phase: phase-07-backend-api.md
"""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..config import get_settings
from ..errors import CoverageIntelError
from ..logging_config import configure_logging
from ..pipeline.rag import answer_question
from .schemas import AskRequest

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
    async def _handle_known_error(_request: Request, exc: CoverageIntelError) -> JSONResponse:
        return _error_response(exc)

    @app.post("/ask")
    async def ask(request: AskRequest) -> object:
        """Answer a coverage question through the RAG pipeline."""
        return answer_question(
            request.question,
            request.scenario,
            query_id=str(uuid4()),
        )

    return app


def _error_response(exc: CoverageIntelError) -> JSONResponse:
    """Build the error envelope. Never includes a partial answer."""
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": exc.error_code,
            "message": str(exc),
            "retryable": exc.retryable,
        },
    )


app = create_app()
