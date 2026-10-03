"""Section-aware, token-aware chunking — FR-04.

Defaults: 500 tokens, 50-token overlap, both configurable.
Invariants C-1..C-5 in specs/04-ingestion.md.

Spec: specs/04-ingestion.md
"""

from __future__ import annotations

from .loaders import Block
from .metadata import Chunk


def chunk(blocks: list[Block], size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split blocks into retrieval units respecting section boundaries."""
    raise NotImplementedError("Implemented in phase-02-ingestion.md")
