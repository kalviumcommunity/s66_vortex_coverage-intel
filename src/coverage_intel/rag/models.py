"""Domain Data Models and Data Transfer Objects (DTOs) for the RAG pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """Represents an atomic text chunk to be embedded and stored in Pinecone."""

    id: str = Field(description="Unique identifier for the vector record (e.g. doc-id#chunk-0)")
    text: str = Field(min_length=1, description="Raw passage text content")
    document_id: str = Field(description="Parent policy or document identifier")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary searchable metadata")


class ScoredRecord(BaseModel):
    """Represents a chunk retrieved from Pinecone with its similarity score."""

    id: str = Field(description="Vector record ID")
    score: float = Field(description="Cosine similarity or retrieval score")
    text: str = Field(description="Passage text content")
    document_id: str = Field(default="", description="Parent document identifier")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Associated chunk metadata")


class Citation(BaseModel):
    """Provenance citation mapping a claim directly back to a retrieved document chunk."""

    index: int = Field(description="Sequential citation reference index [1], [2], etc.")
    document_id: str = Field(description="Source document identifier")
    chunk_id: str = Field(description="Exact chunk identifier")
    score: float = Field(description="Relevance score of the supporting chunk")
    excerpt: str = Field(description="Exact supporting text snippet from the policy")


class RagResponse(BaseModel):
    """Complete enterprise RAG response with grounded answer, citations, and metadata."""

    query: str = Field(description="Original user coverage question")
    answer: str = Field(description="Grounded response synthesized by xAI Grok")
    status: str = Field(description="Grounding status: 'grounded' | 'insufficient_evidence'")
    citations: list[Citation] = Field(default_factory=list, description="Verifiable policy citations")
    model: str = Field(description="xAI Grok model used for answer generation")
    retrieval_count: int = Field(description="Number of chunks retrieved above relevance threshold")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of generation",
    )
    latency_ms: float = Field(default=0.0, description="Total pipeline latency in milliseconds")

