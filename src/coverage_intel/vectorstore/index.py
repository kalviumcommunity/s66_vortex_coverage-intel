"""Vector store behind a provider-agnostic interface — FR-07.

Chroma in development, Qdrant in production, selected via ``CI_VECTOR_STORE``.
Both sit behind ``VectorStore`` so pipeline logic never changes.

Spec: specs/05-retrieval.md
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel

from ..ingestion.metadata import Chunk


class ScoredChunk(BaseModel):
    """A chunk with its similarity score."""

    chunk: Chunk
    score: float


class VectorStore(Protocol):
    """Provider-agnostic vector store interface."""

    @property
    def count(self) -> int: ...

    def upsert(self, chunks: Sequence[Chunk], vectors: list[list[float]]) -> None: ...

    def search(
        self, vector: list[float], k: int, filters: object | None = None
    ) -> list[ScoredChunk]: ...

    def delete_by_document(self, document_id: str) -> None: ...

    def get_chunk(self, chunk_id: str) -> Chunk | None: ...


_DEFAULT_STORE: VectorStore | None = None


def get_vector_store(dimensions: int | None = None) -> VectorStore:
    """Return the configured vector store adapter.

    ``dimensions`` must match the embedding model's output size. When not
    supplied the store is created lazily on first ``upsert`` call.
    """
    global _DEFAULT_STORE
    if _DEFAULT_STORE is None:
        if dimensions is None:
            raise ValueError(
                "vector store dimensions must be supplied on first creation"
            )
        from .memory import InMemoryVectorStore
        from .schema import CollectionSpec

        spec = CollectionSpec(name="coverage-intel", dimensions=dimensions)
        _DEFAULT_STORE = InMemoryVectorStore(spec)
    return _DEFAULT_STORE
