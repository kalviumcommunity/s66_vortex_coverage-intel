"""Pydantic request/response schemas. OpenAPI is generated from these.

Spec: specs/07-api-contract.md
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from ..ingestion.metadata import SourceCategory
from ..retrieval.semantic import Scenario


class AskRequest(BaseModel):
    """A coverage question with optional applicability context."""

    question: str = Field(min_length=1, description="The coverage question")
    scenario: Scenario | None = Field(
        default=None,
        description="Applicability context. date_of_loss drives version resolution.",
    )
    top_k: int = Field(default=5, ge=1, le=20)
    filters: dict | None = None
    conversation_id: str | None = None


class UploadMetadata(BaseModel):
    """Metadata supplied with an approved document upload."""

    document_id: str | None = None
    category: SourceCategory
    version: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    jurisdiction: str | None = None
    linked_policy_id: str | None = None


class UploadAccepted(BaseModel):
    """Response returned when an upload is accepted for processing."""

    document_id: str
    status: str = "processing"
    message: str
