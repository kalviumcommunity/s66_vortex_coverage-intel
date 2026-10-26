"""Hybrid semantic + keyword retrieval — FR-09.

``score_hybrid = a * score_dense + (1 - a) * score_sparse``  (a default 0.7)
Reciprocal Rank Fusion is the documented alternative when the score
distributions are not comparable.

Metadata filters are applied **before** scoring.

Spec: specs/05-retrieval.md
"""

from __future__ import annotations

from .semantic import RetrievedEvidence


def fuse(
    semantic: list[RetrievedEvidence],
    keyword: list[RetrievedEvidence],
    alpha: float = 0.7,
    k: int = 5,
) -> list[RetrievedEvidence]:
    """Fuse dense and sparse results into one ranked list."""
    raise NotImplementedError("Implemented in phase-03-embeddings-and-vector-db.md")
