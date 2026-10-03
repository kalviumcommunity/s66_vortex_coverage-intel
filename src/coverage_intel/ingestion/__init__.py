"""Ingestion: loading, extraction, cleaning, chunking, metadata (FR-01..FR-05).

Spec: specs/04-ingestion.md · Phase: phases/phase-02-ingestion.md
"""

from .loaders import ExtractedDocument, load  # noqa: F401
from .cleaning import clean  # noqa: F401
from .chunking import chunk  # noqa: F401
from .metadata import Chunk, SourceCategory, SourceDocument, attach_metadata  # noqa: F401
