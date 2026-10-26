"""Similarity and distance metrics for embedding vectors."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .encoder import EmbeddingVector


@dataclass(frozen=True, slots=True)
class SimilarityResult:
    """A candidate index and its similarity score."""

    index: int
    score: float


def _check_dimensions(left: EmbeddingVector, right: EmbeddingVector) -> None:
    if left.dimensions != right.dimensions:
        raise ValueError("vectors must have the same dimensionality")


def cosine_similarity(left: EmbeddingVector, right: EmbeddingVector) -> float:
    """Return cosine similarity in the range [-1, 1]."""
    _check_dimensions(left, right)
    denominator = left.norm * right.norm
    if denominator == 0.0:
        raise ValueError("cosine similarity is undefined for zero vectors")
    return sum(a * b for a, b in zip(left.values, right.values, strict=True)) / denominator


def euclidean_distance(left: EmbeddingVector, right: EmbeddingVector) -> float:
    """Return straight-line distance between two vectors."""
    _check_dimensions(left, right)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left.values, right.values, strict=True)))


def rank_by_cosine(
    query: EmbeddingVector, candidates: list[EmbeddingVector]
) -> list[SimilarityResult]:
    """Rank candidate indexes from most to least semantically similar."""
    results = [
        SimilarityResult(index, cosine_similarity(query, candidate))
        for index, candidate in enumerate(candidates)
    ]
    return sorted(results, key=lambda result: result.score, reverse=True)
