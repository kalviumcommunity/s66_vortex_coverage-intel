"""Embedding quality checks — LU 3.29 (Recommended, not MVP-gating).

Detects degenerate representations before they degrade every query:
near-duplicate embeddings, zero-variance vectors, dimensionality anomalies.

Spec: docs/ROADMAP.md · Phase 10
"""

from __future__ import annotations

from statistics import pvariance

from .encoder import Embedder, EmbeddingVector
from .similarity import cosine_similarity


def check_quality(
    embedder: Embedder,
    vectors: list[list[float]],
    *,
    duplicate_threshold: float = 0.999,
) -> dict[str, object]:
    """Report dimensionality, variance, and duplicate-vector anomalies."""
    if not 0.0 <= duplicate_threshold <= 1.0:
        raise ValueError("duplicate_threshold must be between 0.0 and 1.0")
    expected_dimensions = embedder.dimensions
    dimension_mismatches = [
        index for index, vector in enumerate(vectors) if len(vector) != expected_dimensions
    ]
    valid = [
        (index, EmbeddingVector(tuple(vector)))
        for index, vector in enumerate(vectors)
        if len(vector) == expected_dimensions
    ]
    zero_vectors = [index for index, vector in valid if vector.norm == 0.0]
    nonzero_values = [vector.values for _, vector in valid if vector.norm > 0.0]
    variance = (
        [pvariance(values) for values in zip(*nonzero_values, strict=False)]
        if nonzero_values
        else []
    )
    near_duplicates = [
        (left_index, right_index)
        for position, (left_index, left) in enumerate(valid)
        for right_index, right in valid[position + 1 :]
        if left.norm > 0.0
        and right.norm > 0.0
        and cosine_similarity(left, right) >= duplicate_threshold
    ]
    return {
        "count": len(vectors),
        "dimensions": expected_dimensions,
        "dimension_mismatches": dimension_mismatches,
        "zero_vectors": zero_vectors,
        "variance": variance,
        "near_duplicate_pairs": near_duplicates,
        "healthy": bool(vectors)
        and not dimension_mismatches
        and not zero_vectors
        and not near_duplicates,
    }
