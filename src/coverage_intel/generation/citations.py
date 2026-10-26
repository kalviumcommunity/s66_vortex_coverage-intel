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
from ..retrieval.semantic import RetrievedEvidence


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


def build_citations(evidence: list[object], answer: dict[str, object]) -> list[Citation]:
    """Build citations from the cited evidence blocks."""
    statements = answer.get("statements", [])
    cited_indices: set[int] = set()
    if isinstance(statements, list):
        for statement in statements:
            if isinstance(statement, dict):
                indices = statement.get("citation_indices", [])
                if isinstance(indices, list):
                    cited_indices.update(index for index in indices if isinstance(index, int))
    selected = [
        item for index, item in enumerate(evidence) if not cited_indices or index in cited_indices
    ]
    citations: list[Citation] = []
    for citation_index, item in enumerate(selected, 1):
        if not isinstance(item, RetrievedEvidence):
            continue
        chunk = item.chunk
        citations.append(
            Citation(
                citation_index=citation_index,
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                document_title=chunk.document_id,
                section=chunk.section,
                page=chunk.page,
                version=chunk.version,
                effective_from=chunk.effective_from,
                effective_to=chunk.effective_to,
                jurisdiction=chunk.jurisdiction,
                category=chunk.category,
                excerpt=chunk.text,
            )
        )
    return citations
