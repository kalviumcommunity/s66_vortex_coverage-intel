"""Tests for vector collection design."""

from __future__ import annotations

import pytest

from coverage_intel.vectorstore.schema import (
    DEFAULT_METADATA_FIELDS,
    CollectionSpec,
    create_chroma_collection,
)


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def get_or_create_collection(self, name: str, metadata: dict[str, object]) -> object:
        self.calls.append((name, metadata))
        return {"name": name, "metadata": metadata}


def test_collection_factory_declares_dimension_distance_and_metadata() -> None:
    client = FakeClient()
    spec = CollectionSpec(name="coverage_chunks", dimensions=1536)

    collection = create_chroma_collection(client, spec)

    assert collection["name"] == "coverage_chunks"
    assert client.calls[0][1]["hnsw:space"] == "cosine"
    assert client.calls[0][1]["embedding_dimensions"] == 1536
    assert "document_id" in client.calls[0][1]["metadata_fields"]
    assert spec.metadata_fields == DEFAULT_METADATA_FIELDS


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": "", "dimensions": 3},
        {"name": "chunks", "dimensions": 0},
        {"name": "chunks", "dimensions": 3, "distance": "bad"},
    ],
)
def test_collection_spec_rejects_invalid_contracts(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        CollectionSpec(**kwargs)  # type: ignore[arg-type]
