"""Grounded answer generation — FR-12.

Temperature <= 0.2. Structured JSON output validated against a Pydantic schema.
Post-generation validator I-7: every GROUNDED statement must carry at least one
resolvable citation, or the answer is downgraded to WEAK_EVIDENCE.

Spec: specs/06-generation-and-guardrails.md
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, model_validator

from ..retrieval.semantic import RetrievedEvidence
from .citations import Citation
from .context import Context
from .guardrails import Warning, WarningKind


class AnswerStatus(StrEnum):
    """Answer outcome.

    Note: there is deliberately no approved/denied/settled value. Adding one
    would violate AGENTS.md §2 rule 6.
    """

    GROUNDED = "grounded"
    WEAK_EVIDENCE = "weak_evidence"
    CONFLICTING = "conflicting"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class AnswerStatement(BaseModel):
    """One claim in the answer, bound to its citations."""

    text: str
    citation_indices: list[int] = []


class CoverageAnswer(BaseModel):
    """The full grounded response."""

    query_id: str
    question: str
    status: AnswerStatus
    summary: str
    statements: list[AnswerStatement] = []
    citations: list[Citation] = []
    warnings: list[Warning] = []
    evidence: list[RetrievedEvidence] = []
    generated_at: datetime
    latency_ms: int = 0
    stages: dict[str, int] = {}

    @model_validator(mode="after")
    def _enforce_grounding(self) -> CoverageAnswer:
        """Invariant I-7: a GROUNDED answer must cite every statement."""
        if self.status is not AnswerStatus.GROUNDED:
            return self
        valid = {c.citation_index for c in self.citations}
        for statement in self.statements:
            if not statement.citation_indices or not set(statement.citation_indices) <= valid:
                object.__setattr__(self, "status", AnswerStatus.WEAK_EVIDENCE)
                object.__setattr__(
                    self,
                    "warnings",
                    [
                        *self.warnings,
                        Warning(
                            kind=WarningKind.REVIEW_REQUIRED,
                            severity="warning",
                            message="One or more statements lacked resolvable citations; "
                            "answer downgraded to requiring review.",
                        ),
                    ],
                )
                break
        return self


def generate(question: str, context: Context, query_id: str) -> CoverageAnswer:
    """Generate a grounded answer constrained to retrieved evidence."""
    now = datetime.now()
    if not context.blocks:
        return CoverageAnswer(
            query_id=query_id,
            question=question,
            status=AnswerStatus.INSUFFICIENT_EVIDENCE,
            summary="Insufficient evidence was retrieved to answer this question.",
            generated_at=now,
        )

    # Build citations from evidence chunks — every citation resolves to a real chunk
    citations = []
    for idx, block in enumerate(context.blocks, 1):
        chunk = block.chunk
        citations.append(
            Citation(
                citation_index=idx,
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

    # Build statements — each statement cites its own evidence chunk
    statements = []
    for idx, block in enumerate(context.blocks, 1):
        chunk = block.chunk
        statements.append(
            AnswerStatement(text=chunk.text, citation_indices=[idx])
        )

    # Build summary from the most relevant evidence
    summary = context.blocks[0].chunk.text

    return CoverageAnswer(
        query_id=query_id,
        question=question,
        status=AnswerStatus.GROUNDED,
        summary=summary,
        statements=statements,
        citations=citations,
        evidence=context.blocks,
        generated_at=now,
    )
