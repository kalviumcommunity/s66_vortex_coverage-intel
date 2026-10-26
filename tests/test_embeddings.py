"""Tests for embedding vector fundamentals."""

from __future__ import annotations

import pytest

from coverage_intel.embeddings.encoder import EmbeddingVector, validate_batch


def test_embedding_vector_reports_dimension_norm_and_unit_vector() -> None:
    vector = EmbeddingVector((3.0, 4.0))

    assert vector.dimensions == 2
    assert vector.norm == 5.0
    assert vector.normalized().norm == pytest.approx(1.0)


def test_embedding_batch_requires_consistent_dimensions() -> None:
    assert validate_batch([EmbeddingVector((1.0, 2.0)), EmbeddingVector((3.0, 4.0))]) == 2
    with pytest.raises(ValueError, match="same dimensionality"):
        validate_batch([EmbeddingVector((1.0,)), EmbeddingVector((1.0, 2.0))])


@pytest.mark.parametrize("values", [(), (float("nan"),), (float("inf"),)])
def test_invalid_vectors_are_rejected(values: tuple[float, ...]) -> None:
    with pytest.raises(ValueError):
        EmbeddingVector(values)
