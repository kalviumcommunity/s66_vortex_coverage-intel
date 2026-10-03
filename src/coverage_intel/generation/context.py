"""Bounded context assembly — FR-11.

Budget = min(CI_MAX_CONTEXT_TOKENS, model_context_limit - output_reserve).
Evidence ordered by final score. Source identifiers preserved in every block.
Truncation is recorded so the UI can report limited evidence.

Spec: specs/06-generation-and-guardrails.md
"""

from __future__ import annotations

from pydantic import BaseModel

from ..retrieval.semantic import RetrievedEvidence


class Context(BaseModel):
    """Assembled generation context."""

    text: str
    blocks: list[RetrievedEvidence]
    token_count: int
    truncated: bool = False


def assemble(
    evidence: list[RetrievedEvidence], budget: int | None = None
) -> Context:
    """Assemble a bounded context from selected evidence."""
    raise NotImplementedError("Implemented in phase-05-rag-core.md")
