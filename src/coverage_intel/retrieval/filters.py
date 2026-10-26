"""Metadata predicates applied before retrieval scoring."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..ingestion.metadata import Chunk


def matches(chunk: Chunk, filters: Mapping[str, Any] | None) -> bool:
    """Return whether all supplied metadata filters match a chunk."""
    if not filters:
        return True
    metadata = chunk.model_dump()
    return all(metadata.get(key) == value for key, value in filters.items())
