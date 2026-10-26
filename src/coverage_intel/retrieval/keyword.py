"""BM25 keyword retrieval.

Policy language is lexically specific — defined terms, clause numbers — so
keyword retrieval carries signal that pure semantic search drops.

Spec: specs/05-retrieval.md
"""

from __future__ import annotations


from ..ingestion.metadata import Chunk
from .filters import matches
from .semantic import RetrievedEvidence


class KeywordIndex:
    """BM25/lexical keyword index over chunk text."""

    def __init__(self, chunks: list[Chunk] | None = None) -> None:
        self._chunks: list[Chunk] = chunks or []

    def set_chunks(self, chunks: list[Chunk]) -> None:
        self._chunks = list(chunks)

    def search(self, query: str, k: int = 5, filters: object | None = None) -> list[RetrievedEvidence]:
        """Return the top-k chunks by keyword match score."""
        if not self._chunks or k < 1:
            return []
        query_terms = set(query.lower().split())
        if not query_terms:
            return []

        scored: list[tuple[float, Chunk]] = []
        filter_dict = filters if isinstance(filters, dict) else None
        for chunk in self._chunks:
            if not matches(chunk, filter_dict):
                continue
            text_lower = chunk.text.lower()
            words = text_lower.split()
            if not words:
                continue
            matches_count = sum(text_lower.count(term) for term in query_terms)
            if matches_count > 0:
                score = min(1.0, float(matches_count) / float(len(words) ** 0.5))
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievedEvidence(
                chunk=chunk,
                semantic_score=score,
                keyword_score=score,
                hybrid_score=score,
                rank=rank,
            )
            for rank, (score, chunk) in enumerate(scored[:k], start=1)
        ]

