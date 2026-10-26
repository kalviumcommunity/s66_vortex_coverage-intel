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
    if not 0 <= alpha <= 1:
        raise ValueError("alpha must be between 0 and 1")
    if k < 1:
        raise ValueError("k must be positive")
    by_chunk: dict[str, RetrievedEvidence] = {}
    for evidence in semantic:
        by_chunk[evidence.chunk.chunk_id] = evidence.model_copy(
            update={"keyword_score": evidence.keyword_score or 0.0}
        )
    for evidence in keyword:
        current = by_chunk.get(evidence.chunk.chunk_id, evidence)
        by_chunk[evidence.chunk.chunk_id] = current.model_copy(
            update={"keyword_score": evidence.semantic_score}
        )
    fused = [
        evidence.model_copy(
            update={
                "hybrid_score": alpha * evidence.semantic_score
                + (1 - alpha) * (evidence.keyword_score or 0.0)
            }
        )
        for evidence in by_chunk.values()
    ]
    fused.sort(key=lambda item: item.hybrid_score, reverse=True)
    return [item.model_copy(update={"rank": rank}) for rank, item in enumerate(fused[:k], 1)]
