"""Vector collection schema and Chroma collection construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

DEFAULT_METADATA_FIELDS = (
    "document_id",
    "category",
    "version",
    "effective_from",
    "effective_to",
    "jurisdiction",
    "linked_policy_id",
    "section",
    "page",
    "metadata_incomplete",
)


@dataclass(frozen=True, slots=True)
class CollectionSpec:
    """Explicit vector collection contract."""

    name: str
    dimensions: int
    distance: str = "cosine"
    metadata_fields: tuple[str, ...] = DEFAULT_METADATA_FIELDS

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("collection name must not be empty")
        if self.dimensions < 1:
            raise ValueError("collection dimensions must be positive")
        if self.distance not in {"cosine", "l2", "ip"}:
            raise ValueError("distance must be cosine, l2, or ip")
        if not self.metadata_fields:
            raise ValueError("collection must define metadata fields")


class CollectionClient(Protocol):
    """Minimal client interface needed to create a collection."""

    def get_or_create_collection(self, name: str, metadata: dict[str, Any]) -> Any: ...


def create_chroma_collection(client: CollectionClient, spec: CollectionSpec) -> Any:
    """Create or retrieve a Chroma collection with the declared contract."""
    metadata: dict[str, Any] = {
        "hnsw:space": spec.distance,
        "embedding_dimensions": spec.dimensions,
        "metadata_fields": ",".join(spec.metadata_fields),
    }
    return client.get_or_create_collection(name=spec.name, metadata=metadata)
