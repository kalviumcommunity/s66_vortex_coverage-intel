"""API routes — FR-15, FR-16.

Spec: docs/API.md · Phase: phase-07
"""

from __future__ import annotations

from typing import Any


async def ask(request: Any) -> Any:
    """POST /api/v1/ask — coverage question.

    Returns answer, citations, and warnings. ``status != "grounded"`` is a
    valid HTTP 200 response, not an error.
    """
    raise NotImplementedError("Implemented in phase-07-backend-api.md")


async def upload_document(file: Any, metadata: Any, access_key: str | None) -> Any:
    """POST /api/v1/documents/upload — access-key protected runtime indexing."""
    raise NotImplementedError("Implemented in phase-07-backend-api.md")


async def get_document(document_id: str) -> Any:
    """GET /api/v1/documents/{document_id} — ingestion and index status."""
    raise NotImplementedError("Implemented in phase-07-backend-api.md")


async def get_chunk(chunk_id: str) -> Any:
    """GET /api/v1/chunks/{chunk_id} — backs the evidence verification view."""
    raise NotImplementedError("Implemented in phase-07-backend-api.md")


async def health() -> Any:
    """GET /api/v1/health — service and knowledge-base status."""
    raise NotImplementedError("Implemented in phase-07-backend-api.md")
