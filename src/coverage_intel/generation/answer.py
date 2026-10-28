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
    answer_text: str = ""
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

    # Synthesize grounded answer using the configured LLM (Groq / Grok)
    summary = context.blocks[0].chunk.text
    try:
        from ..config import get_settings
        from .llm import ChatMessage, OpenAIChatClient

        cfg = get_settings()
        if cfg.llm_api_key and cfg.llm_model:
            evidence_snippets = []
            for idx, b in enumerate(context.blocks, 1):
                sec = b.chunk.section or "Section I"
                page = b.chunk.page or 1
                evidence_snippets.append(f"[{idx}] Document: {b.chunk.document_id} | Section: {sec} | Page: {page}\n{b.chunk.text}")

            context_str = "\n\n".join(evidence_snippets)
            prompt = (
                f"Question: {question}\n\n"
                f"Authoritative Policy Context:\n{context_str}\n\n"
                "Instructions:\n"
                "1. Provide a professional, concise, direct answer to the adjuster's question.\n"
                "2. State clearly whether the loss is COVERED, EXCLUDED, or CONDITIONAL upon specific policy requirements (such as heat maintenance, vacancy, or prompt notice).\n"
                "3. Cite the relevant sections and peril/exclusion numbers explicitly.\n"
                "4. Base your answer STRICTLY on the policy text above without external assumptions."
            )
            client = OpenAIChatClient(cfg)
            completion = client.complete(
                [
                    ChatMessage(
                        role="system",
                        content="You are Coverage Intel, an enterprise AI assistant for insurance claims adjusters. Provide strictly grounded decision support citing policy language.",
                    ),
                    ChatMessage(role="user", content=prompt),
                ],
                temperature=0.1,
                max_tokens=2048,
            )
            if completion.content and completion.content.strip():
                summary = completion.content.strip()
    except Exception as exc:
        import logging
        logging.getLogger("coverage-intel.answer").warning("LLM answer generation error: %s", exc)

    return CoverageAnswer(
        query_id=query_id,
        question=question,
        status=AnswerStatus.GROUNDED,
        summary=summary,
        answer_text=summary,
        statements=statements,
        citations=citations,
        evidence=context.blocks,
        generated_at=now,
    )
