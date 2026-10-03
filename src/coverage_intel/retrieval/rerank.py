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
