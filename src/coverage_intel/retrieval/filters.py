"""Metadata predicates applied before retrieval scoring."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..ingestion.metadata import Chunk


def matches(chunk: Chunk, filters: Mapping[str, Any] | None) -> bool:
    """Return whether all supplied metadata filters match a chunk."""
    if not filters:
        return True
    metadata = chunk.model_dump()
    for key, value in filters.items():
        if value is None:
            continue
        chunk_val = metadata.get(key)
        if key == "jurisdiction":
            # US-ALL applies universally to all state jurisdictions
            if chunk_val in {"US-ALL", "ALL", None}:
                continue
            clean_val = str(value).upper()
            chunk_clean = str(chunk_val).upper()
            if chunk_clean != clean_val and chunk_clean not in clean_val and clean_val not in chunk_clean:
                return False
        elif key == "policy_type":
            doc_id = str(metadata.get("document_id") or "").upper().replace("-", "")
            val_clean = str(value).upper().replace("-", "")
            category = str(metadata.get("category") or "").lower()
            if (
                val_clean not in doc_id
                and category not in {"endorsement", "claim_guideline", "underwriting_manual"}
                and doc_id not in {"ALL", "UNKNOWN-DOCUMENT"}
            ):
                return False
        elif key in {"claim_type", "date_of_loss"}:
            # Scenario context parameters; do not filter out chunk metadata
            continue
        elif chunk_val != value:
            return False
    return True
