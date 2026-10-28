"""Coverage Service — orchestrates question answering, context retrieval, and decision output."""

from __future__ import annotations

from uuid import uuid4

from ..generation.answer import CoverageAnswer
from ..pipeline.rag import answer_question
from ..retrieval.semantic import Scenario


def ask_coverage(
    question: str,
    scenario: Scenario | None = None,
    query_id: str | None = None,
) -> CoverageAnswer:
    """Answer a coverage inquiry through the verified RAG pipeline."""
    return answer_question(
        question=question,
        scenario=scenario,
        query_id=query_id or str(uuid4()),
    )
