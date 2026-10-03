"""Source documents, chunk metadata, and corpus validation — FR-05.

Invariant I-3: missing ``version`` or ``effective_from`` sets
``metadata_incomplete=True``. Such chunks are **flagged, never dropped**.

Spec: specs/03-data-model.md, specs/04-ingestion.md
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

REQUIRED_TRACEABILITY = ("document_id", "section", "page")
VERSION_FIELDS = ("version", "effective_from")


class SourceCategory(StrEnum):
    """Approved source categories (PRD §4)."""

    POLICY = "policy"
    CLAIM_GUIDELINE = "claim_guideline"
    UNDERWRITING_MANUAL = "underwriting_manual"
    ENDORSEMENT = "endorsement"
    APPROVED_REFERENCE = "approved_reference"


class SourceDocument(BaseModel):
    """A registered source document."""

    document_id: str
    title: str
    category: SourceCategory
    file_type: Literal["pdf", "docx", "txt"]
    version: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    jurisdiction: str | None = None
    authority_rank: int | None = None
    linked_policy_id: str | None = None
    checksum: str
    ingested_at: datetime

    @model_validator(mode="after")
    def _check(self) -> SourceDocument:
        if self.category is SourceCategory.ENDORSEMENT and self.linked_policy_id is None:
            raise ValueError("endorsement documents require linked_policy_id")
        if self.effective_from and self.effective_to and self.effective_from > self.effective_to:
            raise ValueError("effective_from must not be after effective_to")
        return self


class Chunk(BaseModel):
    """A retrieval unit with full provenance."""

    model_config = ConfigDict(frozen=True)

    chunk_id: str
    document_id: str
    text: str
    section: str | None = None
    page: int | None = None
    page_end: int | None = None
    token_count: int
    char_start: int | None = None
    char_end: int | None = None

    category: SourceCategory
    version: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    jurisdiction: str | None = None
    linked_policy_id: str | None = None

    metadata_incomplete: bool = False
    missing_fields: list[str] = []

    @model_validator(mode="after")
    def _flag_incomplete(self) -> Chunk:
        missing = [f for f in VERSION_FIELDS if getattr(self, f) is None]
        if missing and not self.metadata_incomplete:
            object.__setattr__(self, "metadata_incomplete", True)
            object.__setattr__(self, "missing_fields", missing)
        return self


def attach_metadata(chunk: Chunk, document: SourceDocument) -> Chunk:
    """Inherit provenance metadata from the source document."""
    raise NotImplementedError("Implemented in phase-02-ingestion.md")
