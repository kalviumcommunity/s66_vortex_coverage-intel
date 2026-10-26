"""Tests for section-aware token chunking."""

from __future__ import annotations

import pytest

from coverage_intel.ingestion.chunking import TokenChunkingConfig, chunk
from coverage_intel.ingestion.loaders import Block


def test_chunking_respects_size_overlap_and_section_boundaries() -> None:
    blocks = [
        Block(text="one two three four five six seven", section="Coverage", page=1),
        Block(text="eight nine ten", section="Exclusions", page=2),
    ]

    chunks = chunk(blocks, size=4, overlap=1, document_id="policy-1")

    assert chunks
    assert all(item.token_count <= 4 for item in chunks)
    assert {item.section for item in chunks} == {"Coverage", "Exclusions"}
    assert len({item.chunk_id for item in chunks}) == len(chunks)
    assert all(item.document_id == "policy-1" for item in chunks)


def test_chunking_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        chunk([Block(text="text")], size=4, overlap=4)


def test_token_config_enforces_exact_overlap_window() -> None:
    blocks = [Block(text="one two three four five six seven eight nine ten")]
    chunks = chunk(blocks, size=6, overlap=2, model="unknown-model")

    assert TokenChunkingConfig(size=6, overlap=2).overlap == 2
    assert chunks[0].token_count == 6
    assert chunks[1].token_count == 6
