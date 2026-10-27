"""FastAPI application factory.

Phase: phase-07-backend-api.md
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from ..config import get_settings
from ..errors import CoverageIntelError
from ..logging_config import configure_logging
from ..pipeline.rag import answer_question
from .schemas import AskRequest, UploadAccepted, UploadMetadata

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

    @app.middleware("http")
    async def request_id_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Attach a stable request ID to every response."""
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

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

    @app.post("/documents", response_model=UploadAccepted, status_code=202)
    async def register_document(metadata: UploadMetadata) -> UploadAccepted:
        """Accept validated source metadata for asynchronous ingestion."""
        document_id = metadata.document_id or str(uuid4())
        return UploadAccepted(
            document_id=document_id,
            message="Document accepted for ingestion.",
        )

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Report process health without making external provider calls."""
        return {"status": "ok", "service": "coverage-intel"}

    ui_dir = Path(__file__).resolve().parent.parent.parent.parent / "ui"
    if ui_dir.exists():
        from fastapi.responses import RedirectResponse
        from fastapi.staticfiles import StaticFiles

        app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")

        @app.get("/")
        async def root() -> RedirectResponse:
            return RedirectResponse(url="/ui/")

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
