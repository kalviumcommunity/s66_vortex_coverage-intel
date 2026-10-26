"""Embedding encoder behind a provider-agnostic interface — FR-06.

Documents and queries **must** use the same model. A dimension change requires
a full re-index and threshold recalibration.

Spec: specs/05-retrieval.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    """Validated numeric representation of one text input."""

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise ValueError("embedding vectors must contain at least one value")
        if any(not math.isfinite(value) for value in self.values):
            raise ValueError("embedding values must be finite")

    @property
    def dimensions(self) -> int:
        """Return the vector dimensionality."""
        return len(self.values)

    @property
    def norm(self) -> float:
        """Return the Euclidean length."""
        return math.sqrt(sum(value * value for value in self.values))

    def normalized(self) -> EmbeddingVector:
        """Return a unit-length copy, rejecting a zero vector."""
        length = self.norm
        if length == 0.0:
            raise ValueError("zero vectors cannot be normalized")
        return EmbeddingVector(tuple(value / length for value in self.values))


def validate_batch(vectors: list[EmbeddingVector]) -> int:
    """Validate that a batch uses one consistent dimensionality."""
    if not vectors:
        raise ValueError("embedding batch must not be empty")
    dimensions = vectors[0].dimensions
    if any(vector.dimensions != dimensions for vector in vectors[1:]):
        raise ValueError("all embedding vectors must have the same dimensionality")
    return dimensions


class Embedder(Protocol):
    """Provider-agnostic embedding interface."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...

    @property
    def dimensions(self) -> int: ...


def get_embedder() -> Embedder:
    """Return the configured embedding provider."""
    raise NotImplementedError("Implemented in phase-03-embeddings-and-vector-db.md")
