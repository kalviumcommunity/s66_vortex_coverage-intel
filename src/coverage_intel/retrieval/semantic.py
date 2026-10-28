"""Top-K semantic retrieval — FR-08.

Spec: specs/05-retrieval.md
"""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, field_validator

from ..ingestion.metadata import Chunk
from ..vectorstore.index import ScoredChunk, VectorStore


class Scenario(BaseModel):
    """Applicability context supplied by the adjuster."""

    policy_type: str | None = None
    date_of_loss: date | None = None
    jurisdiction: str | None = None
    claim_type: str | None = None

    @field_validator("date_of_loss", mode="before")
    @classmethod
    def parse_empty_date(cls, v: Any) -> Any:
        if v == "" or v is None:
            return None
        return v

    @field_validator("policy_type", "jurisdiction", "claim_type", mode="before")
    @classmethod
    def parse_empty_strings(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class RetrievedEvidence(BaseModel):
    """A retrieved chunk with its scores and rank."""

    chunk: Chunk
    semantic_score: float
    keyword_score: float | None = None
    hybrid_score: float = 0.0
    rerank_score: float | None = None
    rank: int = 0
    retrieval_trace_id: str = ""


def top_k_search(
    store: VectorStore,
    query_vector: list[float],
    k: int = 5,
    trace_id: str = "",
) -> list[RetrievedEvidence]:
    """Convert vector-store results into ranked semantic evidence."""
    if k < 1:
        raise ValueError("k must be positive")
    results: list[ScoredChunk] = store.search(query_vector, k)
    return [
        RetrievedEvidence(
            chunk=result.chunk,
            semantic_score=result.score,
            hybrid_score=result.score,
            rank=rank,
            retrieval_trace_id=trace_id,
        )
        for rank, result in enumerate(results, start=1)
    ]


def retrieve(
    question: str,
    k: int = 5,
    filters: object | None = None,
    scenario: Scenario | dict[str, Any] | None = None,
) -> list[RetrievedEvidence]:
    """Retrieve the top-k chunks with similarity scores and metadata."""
    from ..embeddings.encoder import DeterministicEmbedder, get_embedder
    from ..vectorstore.index import get_vector_store

    try:
        store = get_vector_store()
    except ValueError:
        return []
    if store.count == 0:
        return []
    try:
        embedder = get_embedder()
        query_vector = embedder.embed_query(question)
    except Exception:
        # External embedding API unavailable; fall back to deterministic embedder
        embedder = DeterministicEmbedder(dimensions=1536)
        query_vector = embedder.embed_query(question)

    filter_dict: dict[str, object] = {}
    if isinstance(filters, dict):
        filter_dict.update(filters)
    if scenario:
        jurisdiction = getattr(scenario, "jurisdiction", None) or (scenario.get("jurisdiction") if isinstance(scenario, dict) else None)
        policy_type = getattr(scenario, "policy_type", None) or (scenario.get("policy_type") if isinstance(scenario, dict) else None)
        if jurisdiction:
            filter_dict["jurisdiction"] = jurisdiction
        if policy_type:
            filter_dict["policy_type"] = policy_type

    results = store.search(query_vector, k=k, filters=filter_dict if filter_dict else None)
    return [
        RetrievedEvidence(
            chunk=result.chunk,
            semantic_score=result.score,
            hybrid_score=result.score,
            rank=rank,
        )
        for rank, result in enumerate(results, start=1)
    ]
