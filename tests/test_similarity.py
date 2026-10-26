"""Tests for embedding similarity metrics."""

from __future__ import annotations

import pytest

from coverage_intel.embeddings.encoder import EmbeddingVector
from coverage_intel.embeddings.similarity import (
    cosine_similarity,
    euclidean_distance,
    rank_by_cosine,
)


def test_cosine_similarity_ranks_related_vectors_higher() -> None:
    query = EmbeddingVector((1.0, 0.0, 0.0))
    related = EmbeddingVector((0.9, 0.1, 0.0))
    unrelated = EmbeddingVector((0.0, 0.0, 1.0))

    assert cosine_similarity(query, related) > cosine_similarity(query, unrelated)
    assert rank_by_cosine(query, [unrelated, related])[0].index == 1


def test_distance_and_dimension_validation() -> None:
    assert euclidean_distance(EmbeddingVector((0.0, 0.0)), EmbeddingVector((3.0, 4.0))) == 5.0
    with pytest.raises(ValueError, match="same dimensionality"):
        cosine_similarity(EmbeddingVector((1.0,)), EmbeddingVector((1.0, 2.0)))


def test_zero_vectors_are_rejected_for_cosine() -> None:
    with pytest.raises(ValueError, match="zero vectors"):
        cosine_similarity(EmbeddingVector((0.0, 0.0)), EmbeddingVector((1.0, 0.0)))
