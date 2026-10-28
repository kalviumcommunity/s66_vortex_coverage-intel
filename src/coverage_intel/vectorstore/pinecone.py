"""Pinecone VectorStore adapter implementing the VectorStore protocol."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from pinecone import Pinecone

from ..ingestion.metadata import Chunk, SourceCategory
from ..rag.config import RagSettings
from ..rag.models import DocumentChunk
from ..rag.repositories.vector_repository import VectorRepository
from .index import ScoredChunk, VectorStore

logger = logging.getLogger("coverage-intel.vectorstore.pinecone")


class PineconeVectorStore(VectorStore):
    """Adapter bridging VectorRepository (Pinecone) to the VectorStore protocol."""

    def __init__(self, settings: RagSettings | None = None) -> None:
        cfg = settings or RagSettings()
        self._cfg = cfg
        api_key = (
            cfg.pinecone_api_key.get_secret_value()
            if hasattr(cfg.pinecone_api_key, "get_secret_value")
            else str(cfg.pinecone_api_key)
        )
        self._client = Pinecone(api_key=api_key)
        self._repo = VectorRepository(
            pinecone_client=self._client,
            index_name=cfg.pinecone_index_name,
        )
        self._chunks_cache: dict[str, Chunk] = {}

    @property
    def count(self) -> int:
        """Return total vector count from Pinecone index statistics."""
        try:
            stats = self._repo.describe_index_stats()
            return int(stats.get("total_vector_count", 0))
        except Exception as exc:
            logger.warning("Failed to query Pinecone vector count: %s", exc)
            return len(self._chunks_cache)

    def upsert(self, chunks: Sequence[Chunk], vectors: list[list[float]]) -> None:
        """Convert Chunks + vectors to DocumentChunks and upsert to Pinecone."""
        doc_chunks: list[DocumentChunk] = []
        for chunk, vector in zip(chunks, vectors):
            self._chunks_cache[chunk.chunk_id] = chunk
            metadata = chunk.model_dump(mode="json")
            doc_chunks.append(
                DocumentChunk(
                    id=chunk.chunk_id,
                    vector=vector,
                    text=chunk.text,
                    document_id=chunk.document_id,
                    metadata=metadata,
                )
            )
        self._repo.upsert_chunks(doc_chunks, vectors)

    def search(
        self, vector: list[float], k: int, filters: object | None = None
    ) -> list[ScoredChunk]:
        """Query Pinecone for top-k similar chunks."""
        from ..retrieval.filters import matches

        filter_meta = filters if isinstance(filters, dict) else None
        # Retrieve candidate pool to allow Python post-filtering without dropping valid chunks
        query_k = max(k * 4, 20) if filter_meta else k
        records = self._repo.query_similar(vector, top_k=query_k, filter_dict=None)
        results: list[ScoredChunk] = []

        for r in records:
            cached_chunk = self._chunks_cache.get(r.id)
            if cached_chunk:
                chunk_obj = cached_chunk
            else:
                meta = r.metadata or {}
                chunk_cat = SourceCategory.POLICY
                try:
                    if meta.get("category"):
                        chunk_cat = SourceCategory(meta["category"])
                except Exception:
                    pass
                chunk_obj = Chunk(
                    chunk_id=r.id,
                    document_id=str(meta.get("document_id") or "unknown"),
                    text=r.text or "",
                    category=chunk_cat,
                    section=meta.get("section"),
                    page=meta.get("page"),
                    page_end=meta.get("page_end"),
                    token_count=int(meta.get("token_count") or 100),
                    char_start=meta.get("char_start"),
                    char_end=meta.get("char_end"),
                    version=meta.get("version"),
                    effective_from=meta.get("effective_from"),
                    effective_to=meta.get("effective_to"),
                    jurisdiction=meta.get("jurisdiction"),
                    linked_policy_id=meta.get("linked_policy_id"),
                )

            if filter_meta and not matches(chunk_obj, filter_meta):
                continue

            results.append(ScoredChunk(chunk=chunk_obj, score=r.score))
            if len(results) >= k:
                break

        return results

    def delete_by_document(self, document_id: str) -> None:
        """Delete document vectors from Pinecone."""
        try:
            index = self._repo._get_index()
            index.delete(filter={"document_id": {"$eq": document_id}})
        except Exception as exc:
            logger.warning("Pinecone delete_by_document failed: %s", exc)
        self._chunks_cache = {
            cid: c for cid, c in self._chunks_cache.items() if c.document_id != document_id
        }

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        """Return chunk by ID from cache."""
        return self._chunks_cache.get(chunk_id)
