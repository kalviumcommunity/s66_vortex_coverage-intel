"""Deterministic in-memory vector store used by tests and local development."""

from __future__ import annotations

from collections.abc import Sequence

from ..embeddings.encoder import EmbeddingVector
from ..embeddings.similarity import cosine_similarity
from ..ingestion.metadata import Chunk
from .index import ScoredChunk
from .schema import CollectionSpec


class InMemoryVectorStore:
    """Idempotent chunk/vector store with collection dimension enforcement."""

    def __init__(self, spec: CollectionSpec) -> None:
        self.spec = spec
        self._items: dict[str, tuple[Chunk, EmbeddingVector]] = {}

    def upsert(self, chunks: Sequence[Chunk], vectors: list[list[float]]) -> None:
        """Insert or replace chunks by chunk ID."""
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have equal lengths")
        for chunk, values in zip(chunks, vectors, strict=True):
            vector = EmbeddingVector(tuple(values))
            if vector.dimensions != self.spec.dimensions:
                raise ValueError("vector dimensions do not match collection")
            self._items[chunk.chunk_id] = (chunk, vector)

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        """Return a stored chunk by ID."""
        item = self._items.get(chunk_id)
        return item[0] if item else None

    def get_vector(self, chunk_id: str) -> list[float] | None:
        """Return a stored vector by chunk ID."""
        item = self._items.get(chunk_id)
        return list(item[1].values) if item else None

    def delete_by_document(self, document_id: str) -> None:
        """Delete all chunks belonging to one source document."""
        for chunk_id, (chunk, _) in list(self._items.items()):
            if chunk.document_id == document_id:
                del self._items[chunk_id]

    @property
    def count(self) -> int:
        """Return the number of indexed chunks."""
        return len(self._items)

    def search(self, vector: list[float], k: int) -> list[ScoredChunk]:
        """Return the highest cosine-scored stored chunks."""
        query = EmbeddingVector(tuple(vector))
        if query.dimensions != self.spec.dimensions:
            raise ValueError("query dimensions do not match collection")
        results = [
            ScoredChunk(chunk=chunk, score=cosine_similarity(query, stored))
            for chunk, stored in self._items.values()
        ]
        return sorted(results, key=lambda result: result.score, reverse=True)[:k]
