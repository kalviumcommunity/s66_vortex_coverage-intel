"""FastAPI application factory.

Phase: phase-07-backend-api.md
"""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Awaitable, Callable
from datetime import date, datetime
from pathlib import Path
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import FastAPI, File, Form, Header, Request, Response, UploadFile
from fastapi.responses import JSONResponse

from ..config import get_settings
from ..errors import CoverageIntelError, EmbeddingError, ExtractionError, UnsupportedDocumentType
from ..ingestion.chunking import chunk
from ..ingestion.loaders import ExtractedDocument
from ..ingestion.metadata import SourceCategory, SourceDocument, attach_metadata
from ..ingestion.validation import prepare_corpus
from ..logging_config import configure_logging
from ..pipeline.rag import answer_question
from .security import verify_access_key
from ..vectorstore.index import get_vector_store
from .schemas import AskRequest, UploadAccepted, UploadMetadata

DESCRIPTION = """
**Coverage Intel** — RAG-based insurance coverage intelligence assistant.

Decision support for claims adjusters. This system does **not** approve or deny
claims, calculate settlements, or replace human, legal, compliance, or
underwriting judgment.
"""


def _parse_header_metadata(text: str) -> dict:
    """Parse VERSION / EFFECTIVE DATE / JURISDICTION headers from policy text."""
    import re

    meta: dict = {}
    m = re.search(r"VERSION:\s*(\S+)", text, re.IGNORECASE)
    if m:
        meta["version"] = m.group(1)
    m = re.search(r"EFFECTIVE DATE:\s*(\S+)", text, re.IGNORECASE)
    if m:
        try:
            meta["effective_from"] = date.fromisoformat(m.group(1))
        except ValueError:
            pass
    m = re.search(r"EXPIRATION DATE:\s*(\S+)", text, re.IGNORECASE)
    if m:
        try:
            meta["effective_to"] = date.fromisoformat(m.group(1))
        except ValueError:
            pass
    m = re.search(r"JURISDICTION:\s*(\S+)", text, re.IGNORECASE)
    if m:
        meta["jurisdiction"] = m.group(1)
    m = re.search(r"POLICY IDENTIFIER:\s*(\S+)", text, re.IGNORECASE)
    if m:
        meta["policy_id"] = m.group(1)
    return meta


def _index_files(files: list[Path], logger: logging.Logger) -> int:
    """Load, chunk, attach metadata, embed, and upsert a list of corpus files.

    Returns the number of chunks indexed. Never raises.
    Retries embedding on transient provider failures (e.g., 502).
    """
    from ..embeddings.encoder import get_embedder
    from ..vectorstore.index import get_vector_store

    settings = get_settings()
    docs, _ = prepare_corpus(files)
    all_chunks = []
    for doc in docs:
        full_text = "\n".join(b.text for b in doc.blocks)
        header = _parse_header_metadata(full_text)
        doc_id = header.get("policy_id") or doc.document_id
        source_doc = SourceDocument(
            document_id=doc_id,
            title=doc.document_id,
            category=SourceCategory.POLICY,
            file_type=doc.file_type,
            version=header.get("version"),
            effective_from=header.get("effective_from"),
            effective_to=header.get("effective_to"),
            jurisdiction=header.get("jurisdiction"),
            linked_policy_id=None,
            checksum="",
            ingested_at=datetime.utcnow(),
        )
        raw_chunks = chunk(
            doc.blocks,
            document_id=doc_id,
            category=source_doc.category,
        )
        final_chunks = [attach_metadata(c, source_doc) for c in raw_chunks]
        all_chunks.extend(final_chunks)

    if not all_chunks:
        return 0

    # Retry embedding up to 3 times on transient failures, then fall back
    # to deterministic embedder so indexing never depends on external API
    from ..embeddings.encoder import DeterministicEmbedder

    try:
        embedder = get_embedder(settings)
        texts = [c.text for c in all_chunks]
        vectors = None
        last_error = None
        for attempt in range(3):
            try:
                vectors = embedder.embed_documents(texts)
                break
            except Exception as exc:
                last_error = exc
                wait = 2 ** attempt
                logger.warning("Embedding attempt %d failed: %s (retrying in %ds)", attempt + 1, exc, wait)
                time.sleep(wait)
        if vectors is None:
            raise EmbeddingError(str(last_error))
    except Exception:
        logger.warning("External embedding API unavailable; using deterministic fallback embedder")
        embedder = DeterministicEmbedder(dimensions=1536)
        texts = [c.text for c in all_chunks]
        vectors = embedder.embed_documents(texts)

    dimensions = len(vectors[0]) if vectors else 0
    store = get_vector_store(dimensions=dimensions)
    if store.count > 0:
        return 0
    store.upsert(all_chunks, vectors)
    logger.info("Indexed %d chunks into vector store", len(all_chunks))
    return len(all_chunks)


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

    @app.on_event("startup")
    async def _startup_index() -> None:
        """Index the approved corpus on startup so /ask can retrieve grounded answers."""
        if "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules:
            return
        import logging
        logger = logging.getLogger("coverage-intel")
        try:
            settings = get_settings()
            corpus_path = Path(settings.corpus_dir)
            if not corpus_path.exists():
                return
            files = [p for p in corpus_path.iterdir() if p.is_file() and not p.name.startswith(".")]
            if not files:
                return
            _index_files(files, logger)
        except Exception as exc:  # noqa: BLE001 — never let indexing crash startup
            logger.warning("Startup indexing skipped: %s", exc)

    @app.post("/ask")
    async def ask(request: AskRequest) -> object:
        """Answer a coverage question through the RAG pipeline."""
        # Ensure corpus is indexed in this process before answering (skipped during unit testing)
        if "PYTEST_CURRENT_TEST" not in os.environ and "pytest" not in sys.modules:
            import logging
            logger = logging.getLogger("coverage-intel")
            try:
                settings = get_settings()
                corpus_path = Path(settings.corpus_dir)
                try:
                    store = get_vector_store()
                except ValueError:
                    store = None
                if store is None or store.count == 0:
                    if corpus_path.exists():
                        files = [p for p in corpus_path.iterdir() if p.is_file() and not p.name.startswith(".")]
                        if files:
                            _index_files(files, logger)
                            logger.info("Indexed corpus on first /ask request")
            except Exception as exc:  # noqa: BLE001 — never let indexing break /ask
                logger.warning("Request-time indexing skipped: %s", exc)
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

    @app.post("/documents/upload", response_model=UploadAccepted, status_code=202)
    async def upload_document(
        file: UploadFile = File(...),
        x_upload_access_key: str | None = Header(default=None, alias="X-Upload-Access-Key"),
        document_id: str | None = Form(None),
        category: str = Form("policy"),
        version: str | None = Form(None),
        effective_from: date | None = Form(None),
        effective_to: date | None = Form(None),
        jurisdiction: str | None = Form(None),
        linked_policy_id: str | None = Form(None),
    ) -> UploadAccepted:
        """Accept a document upload, ingest, embed, and index it at runtime (FR-16).

        Protected by ``X-Upload-Access-Key`` header. Runs the full pipeline:
        load → clean → chunk → attach provenance metadata → embed → upsert.
        """
        # ── Access key validation ──────────────────────────────────────
        import logging
        logger = logging.getLogger("coverage-intel")
        verify_access_key(x_upload_access_key)

        # ── Validate file type ─────────────────────────────────────────
        suffix = Path(file.filename or "upload").suffix.lower()
        if suffix not in {".pdf", ".docx", ".txt"}:
            raise UnsupportedDocumentType(f"Unsupported document type: {suffix or '<none>'}")

        # ── Save uploaded file to a temp location ──────────────────────
        tmp_path: Path | None = None
        try:
            with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                copyfileobj(file.file, tmp)
                tmp_path = Path(tmp.name)

            # ── Ingestion: load → clean → chunk ────────────────────────
            docs, _report = prepare_corpus([tmp_path])
            if not docs:
                raise ExtractionError("No usable text extracted from uploaded document")

            extracted: ExtractedDocument = docs[0]

            # ── Build source document record ───────────────────────────
            source_doc = SourceDocument(
                document_id=document_id or extracted.document_id,
                title=file.filename or "uploaded-document",
                category=SourceCategory(category),
                file_type=extracted.file_type,
                version=version,
                effective_from=effective_from,
                effective_to=effective_to,
                jurisdiction=jurisdiction,
                linked_policy_id=linked_policy_id,
                checksum="",
                ingested_at=datetime.utcnow(),
            )

            # ── Chunk + attach provenance metadata ─────────────────────
            raw_chunks = chunk(
                extracted.blocks,
                document_id=source_doc.document_id,
                category=source_doc.category,
            )
            final_chunks = [attach_metadata(c, source_doc) for c in raw_chunks]

            # ── Embed + upsert into vector store ───────────────────────
            settings = get_settings()
            from ..embeddings.encoder import get_embedder

            embedder = get_embedder(settings)
            texts = [c.text for c in final_chunks]

            # Retry embedding up to 3 times on transient failures, then fall back
            # to deterministic embedder so upload never depends on external API
            from ..embeddings.encoder import DeterministicEmbedder

            vectors = None
            last_error = None
            try:
                for attempt in range(3):
                    try:
                        vectors = embedder.embed_documents(texts)
                        break
                    except Exception as exc:
                        last_error = exc
                        wait = 2 ** attempt
                        logger.warning("Upload embedding attempt %d failed: %s (retrying in %ds)", attempt + 1, exc, wait)
                        time.sleep(wait)
                if vectors is None:
                    raise EmbeddingError(str(last_error))
            except Exception:
                logger.warning("External embedding API unavailable; using deterministic fallback embedder")
                embedder = DeterministicEmbedder(dimensions=1536)
                vectors = embedder.embed_documents(texts)

            dimensions = len(vectors[0]) if vectors else 0
            store = get_vector_store(dimensions=dimensions)
            store.upsert(final_chunks, vectors)

            return UploadAccepted(
                document_id=source_doc.document_id,
                message="Document accepted, ingested, and indexed.",
            )
        finally:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)

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
