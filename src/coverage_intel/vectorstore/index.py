"""Vector store behind a provider-agnostic interface — FR-07.

Chroma in development, Qdrant in production, selected via ``CI_VECTOR_STORE``.
Both sit behind ``VectorStore`` so pipeline logic never changes.

Spec: specs/05-retrieval.md
"""

from __future__ import annotations

from typing import Protocol, Sequence

from pydantic import BaseModel

from ..ingestion.metadata import Chunk


class ScoredChunk(BaseModel):
    """A chunk with its similarity score."""

    chunk: Chunk
    score: float


class VectorStore(Protocol):
    """Provider-agnostic vector store interface."""

    def upsert(self, chunks: Sequence[Chunk], vectors: list[list[float]]) -> None: ...

    def search(
        self, vector: list[float], k: int, filters: "object | None" = None
    ) -> list[ScoredChunk]: ...

    def delete_by_document(self, document_id: str) -> None: ...

    def get_chunk(self, chunk_id: str) -> Chunk | None: ...


def get_vector_store() -> VectorStore:
    """Return the configured vector store adapter."""
    raise NotImplementedError("Implemented in phase-03-embeddings-and-vector-db.md")
