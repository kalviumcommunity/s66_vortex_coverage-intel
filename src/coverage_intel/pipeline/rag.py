"""End-to-end RAG pipeline.

Every /ask request runs through here. A stage may be bypassed only by explicit
configuration, and bypassing must be visible in the response payload.

Spec: AGENTS.md §5 · Phase: phase-05
"""

from __future__ import annotations

from ..retrieval.semantic import Scenario


def answer_question(question: str, scenario: Scenario | None = None) -> object:
    """Run the full RAG pipeline and return a CoverageAnswer."""
    raise NotImplementedError("Implemented in phase-05-rag-core.md")
