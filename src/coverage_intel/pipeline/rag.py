"""End-to-end RAG pipeline.

Every /ask request runs through here. A stage may be bypassed only by explicit
configuration, and bypassing must be visible in the response payload.

Spec: AGENTS.md §5 · Phase: phase-05
"""

from __future__ import annotations

from collections.abc import Callable

from ..generation.answer import CoverageAnswer, generate
from ..generation.context import assemble
from ..retrieval.semantic import RetrievedEvidence, Scenario


def answer_question(
    question: str,
    scenario: Scenario | None = None,
    *,
    retriever: Callable[[str, Scenario | None], list[RetrievedEvidence]] | None = None,
    query_id: str = "local-query",
) -> CoverageAnswer:
    """Run the full RAG pipeline and return a CoverageAnswer."""
    if retriever:
        evidence = retriever(question, scenario)
    else:
        from ..retrieval.semantic import retrieve

        evidence = retrieve(question, scenario=scenario)
    context = assemble(evidence)
    return generate(question, context, query_id)
