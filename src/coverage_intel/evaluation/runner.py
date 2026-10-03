"""Repeatable evaluation runner — FR-18.

Reports every PRD §5 metric. Re-run on any change to chunking, embeddings,
top-K, filters, thresholds, reranking, generation model, temperature, prompts,
or corpus. A change that improves one metric while degrading another is not a pass.

Phase: phase-06-rag-evaluation.md
"""

from __future__ import annotations

from typing import Any


def run_suite(suite: str = "golden", compare_to: str | None = None) -> dict[str, Any]:
    """Run the golden evaluation suite and return the metric report."""
    raise NotImplementedError("Implemented in phase-06-rag-evaluation.md")
