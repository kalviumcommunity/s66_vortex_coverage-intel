"""Domain types. Authoritative definitions live in specs/03-data-model.md."""

from __future__ import annotations

from .ingestion.metadata import Chunk, SourceDocument, SourceCategory  # noqa: F401
from .generation.answer import (  # noqa: F401
    AnswerStatus,
    AnswerStatement,
    CoverageAnswer,
)
from .generation.citations import Citation  # noqa: F401
from .generation.guardrails import Warning, WarningKind  # noqa: F401
from .retrieval.semantic import RetrievedEvidence  # noqa: F401
