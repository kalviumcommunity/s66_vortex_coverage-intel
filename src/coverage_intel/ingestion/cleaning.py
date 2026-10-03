"""Boilerplate removal and normalisation — FR-03.

Removes page headers/footers, standalone page numbers, and watermarks.
Preserves clause references, defined terms, negation, and amounts.

Spec: specs/04-ingestion.md
"""

from __future__ import annotations

from .loaders import Block


def clean(blocks: list[Block]) -> list[Block]:
    """Clean extracted blocks without losing coverage-meaningful content."""
    raise NotImplementedError("Implemented in phase-02-ingestion.md")
