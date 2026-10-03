"""Top-K semantic retrieval — FR-08.

Spec: specs/05-retrieval.md
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from ..ingestion.metadata import Chunk


class Scenario(BaseModel):
    """Applicability context supplied by the adjuster.

    ``date_of_loss`` drives version resolution (US-04). When absent, version
    applicability cannot be asserted and a warning is emitted — the system does
    not assume "current version".
    """

    policy_type: str | None = None
    date_of_loss: date | None = None
    jurisdiction: str | None = None
    claim_type: str | None = None


class RetrievedEvidence(BaseModel):
    """A retrieved chunk with its scores and rank."""

    chunk: Chunk
    semantic_score: float
    keyword_score: float | None = None
    hybrid_score: float = 0.0
    rerank_score: float | None = None
    rank: int = 0
    retrieval_trace_id: str = ""


def retrieve(
    question: str,
    k: int = 5,
    filters: "object | None" = None,
    scenario: Scenario | None = None,
) -> list[RetrievedEvidence]:
    """Retrieve the top-k chunks with similarity scores and metadata."""
    raise NotImplementedError("Implemented in phase-03-embeddings-and-vector-db.md")
