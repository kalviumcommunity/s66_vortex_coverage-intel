"""Metric definitions. Authoritative in specs/08-evaluation.md.

E-1  citation_resolution is 1.00 or fail — never averaged.
E-2  answers with status != grounded are excluded from the grounded-rate
    denominator and scored under uncertainty_handling instead.
E-3  a statement with zero citations counts against grounded-answer rate,
    not citation precision.
E-7  cold starts excluded from p95 are reported separately.
"""

from __future__ import annotations


def retrieval_recall_at_k(expected: list[str], retrieved: list[str], k: int = 5) -> float:
    """Fraction of expected chunks present in the top-k retrieved results."""
    if not expected:
        return 0.0
    top = set(retrieved[:k])
    return len(top & set(expected)) / len(expected)


def grounded_answer_rate(answers: list, unsupported_claims: list[str]) -> float:
    """Share of grounded answers containing no unsupported claim."""
    grounded = [a for a in answers if getattr(a, "status", None) == "grounded"]
    if not grounded:
        return 0.0
    bad = {getattr(a, "query_id", None) for a in unsupported_claims}
    return sum(1 for a in grounded if a.query_id not in bad) / len(grounded)


def uncertainty_handling(questions: list, answers: list) -> float:
    """Share of insufficient/conflicting questions answered with a review response."""
    relevant = [q for q in questions if q.get("category") in
                ("insufficient_evidence", "version_conflict")]
    if not relevant:
        return 0.0
    by_id = {getattr(a, "query_id", None): getattr(a, "status", None) for a in answers}
    return sum(
        1 for q in relevant
        if by_id.get(q["qid"]) not in ("grounded", None)
    ) / len(relevant)


def percentile(values: list[float], p: float) -> float:
    """Compute a percentile. Used for P95 latency reporting."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(int(len(ordered) * p / 100), len(ordered) - 1)
    return ordered[index]
