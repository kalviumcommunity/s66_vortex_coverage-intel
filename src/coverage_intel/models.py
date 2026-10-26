"""Domain types. Authoritative definitions live in specs/03-data-model.md."""

from __future__ import annotations

from .generation.answer import (  # noqa: F401
    AnswerStatement,
    AnswerStatus,
    CoverageAnswer,
)
from .generation.citations import Citation  # noqa: F401
from .generation.guardrails import Warning, WarningKind  # noqa: F401
from .ingestion.metadata import Chunk, SourceCategory, SourceDocument  # noqa: F401
from .retrieval.semantic import RetrievedEvidence  # noqa: F401
