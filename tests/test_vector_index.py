"""Tests for embedding and metadata indexing."""

from __future__ import annotations

import pytest

from coverage_intel.ingestion.metadata import Chunk, SourceCategory
from coverage_intel.vectorstore.memory import InMemoryVectorStore
from coverage_intel.vectorstore.schema import CollectionSpec


def _chunk(chunk_id: str, document_id: str = "doc-1") -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        document_id=document_id,
        text=chunk_id,
        token_count=1,
        category=SourceCategory.POLICY,
    )


def test_upsert_is_idempotent_and_round_trips_metadata() -> None:
    store = InMemoryVectorStore(CollectionSpec("chunks", dimensions=2))
    chunk = _chunk("chunk-1")
    store.upsert([chunk], [[1.0, 0.0]])
    store.upsert([chunk], [[1.0, 0.0]])

    assert store.count == 1
    assert store.get_chunk("chunk-1") == chunk
    assert store.get_vector("chunk-1") == [1.0, 0.0]


def test_index_rejects_mismatched_dimensions_and_deletes_by_document() -> None:
    store = InMemoryVectorStore(CollectionSpec("chunks", dimensions=2))
    with pytest.raises(ValueError, match="dimensions"):
        store.upsert([_chunk("bad")], [[1.0]])
    store.upsert([_chunk("one"), _chunk("two", "doc-2")], [[1.0, 0.0], [0.0, 1.0]])
    store.delete_by_document("doc-1")
    assert store.count == 1
    assert store.get_chunk("one") is None
