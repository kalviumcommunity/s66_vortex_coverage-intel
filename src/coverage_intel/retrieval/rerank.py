"""Cross-encoder re-ranking — LU 3.35 (Recommended, not MVP-gating).

Reranks the top ``CI_RERANK_TOP_N`` candidates down to final K.
Disabled by default. Retrieval must meet recall@5 **without** it.

Spec: phases/phase-10-recommended-and-optional.md
"""

from __future__ import annotations

from typing import Protocol

from .semantic import RetrievedEvidence


class Reranker(Protocol):
    """Provider-agnostic reranker interface."""

    def rerank(
        self, query: str, evidence: list[RetrievedEvidence], k: int
    ) -> list[RetrievedEvidence]: ...


class LexicalReranker:
    """Small deterministic fallback reranker for local use and tests."""

    def rerank(
        self, query: str, evidence: list[RetrievedEvidence], k: int
    ) -> list[RetrievedEvidence]:
        if k < 1:
            raise ValueError("k must be positive")
        terms = set(query.lower().split())
        ranked = [
            item.model_copy(
                update={
                    "rerank_score": sum(term in item.chunk.text.lower().split() for term in terms)
                }
            )
            for item in evidence
        ]
        ranked.sort(key=lambda item: (item.rerank_score or 0, item.hybrid_score), reverse=True)
        return [item.model_copy(update={"rank": rank}) for rank, item in enumerate(ranked[:k], 1)]
