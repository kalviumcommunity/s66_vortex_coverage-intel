"""Tests for chunk source metadata and traceability."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from coverage_intel.ingestion.metadata import (
    Chunk,
    SourceCategory,
    SourceDocument,
    attach_metadata,
)


def _document(**overrides: object) -> SourceDocument:
    values: dict[str, object] = {
        "document_id": "policy-1",
        "title": "Home policy",
        "category": SourceCategory.POLICY,
        "file_type": "txt",
        "version": "2026.1",
        "effective_from": date(2026, 1, 1),
        "checksum": "abc123",
        "ingested_at": datetime.now(UTC),
    }
    values.update(overrides)
    return SourceDocument.model_validate(values)


def _chunk() -> Chunk:
    return Chunk(
        chunk_id="chunk-1",
        document_id="unknown-document",
        text="Coverage language",
        section="Coverage",
        page=2,
        token_count=2,
        category=SourceCategory.APPROVED_REFERENCE,
    )


def test_attach_metadata_copies_source_identity_and_dates() -> None:
    result = attach_metadata(_chunk(), _document(jurisdiction="TX", linked_policy_id="home-1"))

    assert result.document_id == "policy-1"
    assert result.category is SourceCategory.POLICY
    assert result.version == "2026.1"
    assert result.jurisdiction == "TX"
    assert result.linked_policy_id == "home-1"
    assert result.metadata_incomplete is False


def test_missing_version_or_effective_date_flags_but_keeps_chunk() -> None:
    result = attach_metadata(_chunk(), _document(version=None, effective_from=None))

    assert result.metadata_incomplete is True
    assert set(result.missing_fields) == {"version", "effective_from"}


def test_mismatched_source_document_is_rejected() -> None:
    mismatched = _chunk().model_copy(update={"document_id": "other"})
    with pytest.raises(ValueError, match="does not match"):
        attach_metadata(mismatched, _document())
