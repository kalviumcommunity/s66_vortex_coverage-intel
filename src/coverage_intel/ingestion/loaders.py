"""Document loading and text extraction — FR-01, FR-02.

Spec: specs/04-ingestion.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel

SUPPORTED_TYPES: frozenset[str] = frozenset({"pdf", "docx", "txt"})


class Block(BaseModel):
    """A contiguous span of extracted text with its structural provenance.

    Blocks — not one flat string — are what make section- and page-aware
    chunking possible (FR-02, FR-04).
    """

    text: str
    section: str | None = None
    page: int | None = None
    char_start: int | None = None
    char_end: int | None = None


class ExtractedDocument(BaseModel):
    """Result of extracting one source document."""

    document_id: str
    file_type: Literal["pdf", "docx", "txt"]
    blocks: list[Block]
    char_count: int


class DocumentLoader(Protocol):
    """Provider-agnostic loader interface."""

    def load(self, path: Path) -> ExtractedDocument: ...


def load(path: Path) -> ExtractedDocument:
    """Load and extract text from a PDF, DOCX, or TXT file."""
    raise NotImplementedError("Implemented in phase-02-ingestion.md")
