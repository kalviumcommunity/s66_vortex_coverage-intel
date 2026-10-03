"""Citation extraction and verification — FR-13.

``Citation.excerpt`` is copied **verbatim** from the indexed chunk so the
adjuster can verify exact policy wording. A paraphrase is a defect.
Every citation must resolve to a real chunk.

Spec: specs/06-generation-and-guardrails.md
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from ..ingestion.metadata import SourceCategory


class Citation(BaseModel):
    """A source reference backing an answer statement."""

    citation_index: int
    chunk_id: str
    document_id: str
    document_title: str
    section: str | None = None
    page: int | None = None
    version: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    jurisdiction: str | None = None
    category: SourceCategory | None = None
    excerpt: str


def build_citations(evidence: list, answer: dict) -> list[Citation]:
    """Build citations from the cited evidence blocks."""
    raise NotImplementedError("Implemented in phase-05-rag-core.md")
