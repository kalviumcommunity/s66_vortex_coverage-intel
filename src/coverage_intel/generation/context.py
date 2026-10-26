"""Bounded context assembly — FR-11.

Budget = min(CI_MAX_CONTEXT_TOKENS, model_context_limit - output_reserve).
Evidence ordered by final score. Source identifiers preserved in every block.
Truncation is recorded so the UI can report limited evidence.

Spec: specs/06-generation-and-guardrails.md
"""

from __future__ import annotations

from pydantic import BaseModel

from ..retrieval.semantic import RetrievedEvidence
from .tokens import TokenCounter


class Context(BaseModel):
    """Assembled generation context."""

    text: str
    blocks: list[RetrievedEvidence]
    token_count: int
    truncated: bool = False


def assemble(evidence: list[RetrievedEvidence], budget: int | None = None) -> Context:
    """Assemble a bounded context from selected evidence."""
    if budget is not None and budget < 1:
        raise ValueError("budget must be positive")
    counter = TokenCounter()
    selected: list[RetrievedEvidence] = []
    blocks: list[str] = []
    used = 0
    truncated = False
    for item in evidence:
        block = f"[{item.chunk.chunk_id}] {item.chunk.text}"
        tokens = counter.count_text(block)
        if budget is not None and used + tokens > budget:
            truncated = True
            break
        selected.append(item)
        blocks.append(block)
        used += tokens
    return Context(text="\n\n".join(blocks), blocks=selected, token_count=used, truncated=truncated)
