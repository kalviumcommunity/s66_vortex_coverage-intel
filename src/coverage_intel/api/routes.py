"""API routes — FR-15, FR-16.

Spec: docs/API.md · Phase: phase-07
"""

from __future__ import annotations

from typing import Any

from ..services.coverage_service import ask_coverage
from ..services.document_service import process_document_upload
from ..vectorstore.index import get_vector_store
from .security import verify_access_key


async def ask(request: Any) -> Any:
    """POST /api/v1/ask — coverage question.

    Returns answer, citations, and warnings. ``status != "grounded"`` is a
    valid HTTP 200 response, not an error.
    """
    question = getattr(request, "question", str(request))
    scenario = getattr(request, "scenario", None)
    return ask_coverage(question=question, scenario=scenario)


async def upload_document(file: Any, metadata: Any, access_key: str | None) -> Any:
    """POST /api/v1/documents/upload — access-key protected runtime indexing."""
    verify_access_key(access_key)
    filename = getattr(file, "filename", "upload")
    file_stream = getattr(file, "file", file)
    return process_document_upload(
        file_stream=file_stream,
        filename=filename,
        document_id=getattr(metadata, "document_id", None),
        category=getattr(metadata, "category", "policy"),
        version=getattr(metadata, "version", None),
        jurisdiction=getattr(metadata, "jurisdiction", None),
    )


async def get_document(document_id: str) -> Any:
    """GET /api/v1/documents/{document_id} — ingestion and index status."""
    store = get_vector_store()
    return {"document_id": document_id, "indexed_chunks": store.count}


async def get_chunk(chunk_id: str) -> Any:
    """GET /api/v1/chunks/{chunk_id} — backs the evidence verification view."""
    store = get_vector_store()
    chunk = store.get_chunk(chunk_id)
    if not chunk:
        return None
    return chunk


async def health() -> dict[str, str]:
    """GET /api/v1/health — service and knowledge-base status."""
    return {"status": "ok", "service": "coverage-intel"}
