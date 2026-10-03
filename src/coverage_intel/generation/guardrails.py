"""Guardrails, warnings, and applicability analysis — FR-14.

Evaluated **before** generation. First trigger wins.

The system must never degrade to an unevidenced answer. Precedence is resolved
only from validated metadata — **never** from similarity score.

Spec: specs/06-generation-and-guardrails.md · Phase: phase-05
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel


class WarningKind(StrEnum):
    """Warning categories surfaced to the adjuster."""

    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LOW_SIMILARITY = "low_similarity"
    CONFLICTING_SOURCES = "conflicting_sources"
    VERSION_CONFLICT = "version_conflict"
    SUPERSEDED_VERSION = "superseded_version"
    ENDORSEMENT_APPLIES = "endorsement_applies"
    EXCLUSION_FOUND = "exclusion_found"
    METADATA_INCOMPLETE = "metadata_incomplete"
    REVIEW_REQUIRED = "review_required"


class Warning(BaseModel):
    """A warning surfaced with the answer."""

    kind: WarningKind
    severity: Literal["info", "warning", "blocking"]
    message: str
    chunk_ids: list[str] = []
    detail: dict[str, Any] = {}


class GuardrailResult(BaseModel):
    """Outcome of guardrail evaluation."""

    triggered: bool = False
    blocked: bool = False
    warnings: list[Warning] = []


def evaluate(evidence: list, analysis: Any = None) -> GuardrailResult:
    """Evaluate guardrails against retrieved evidence. First trigger wins.

    Triggers, in order:
      1. no evidence retrieved
      2. top semantic score < CI_SIMILARITY_THRESHOLD
      3. no chunk >= CI_RELEVANCE_FLOOR
      4. unresolved conflict
      5. all supporting chunks metadata_incomplete
    """
    raise NotImplementedError("Implemented in phase-05-rag-core.md")


def analyse(evidence: list, scenario: Any = None) -> Any:
    """Applicability and conflict analysis — PRD §9.1.

    Precedence rule (provisional, awaiting confirmation — specs/09):
      1. An endorsement overrides the base policy it is linked to.
      2. Among versions of the same document, the one in effect on the date of
         loss applies.
    """
    raise NotImplementedError("Implemented in phase-05-rag-core.md")
