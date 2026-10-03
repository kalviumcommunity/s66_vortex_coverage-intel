"""Embedding encoder behind a provider-agnostic interface — FR-06.

Documents and queries **must** use the same model. A dimension change requires
a full re-index and threshold recalibration.

Spec: specs/05-retrieval.md
"""

from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    """Provider-agnostic embedding interface."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...

    @property
    def dimensions(self) -> int: ...


def get_embedder() -> Embedder:
    """Return the configured embedding provider."""
    raise NotImplementedError("Implemented in phase-03-embeddings-and-vector-db.md")
