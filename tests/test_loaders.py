"""Tests for multi-format document loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from coverage_intel.errors import CorpusValidationError, UnsupportedDocumentType
from coverage_intel.ingestion.loaders import load


def test_txt_loader_preserves_identity_sections_and_positions(tmp_path: Path) -> None:
    path = tmp_path / "HO Policy.txt"
    path.write_text("COVERAGE A\nSection 7.2\nLoss means direct damage.\n", encoding="utf-8")

    document = load(path)

    assert document.document_id.startswith("ho-policy-")
    assert document.file_type == "txt"
    assert document.blocks[1].section == "Section 7.2"
    assert document.blocks[-1].page == 1
    assert document.blocks[-1].char_start < document.blocks[-1].char_end


def test_same_content_has_stable_identity(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("same policy", encoding="utf-8")
    second.write_text("same policy", encoding="utf-8")

    assert load(first).document_id != load(second).document_id
    assert load(first).document_id == load(first).document_id


def test_unsupported_and_empty_documents_fail(tmp_path: Path) -> None:
    unsupported = tmp_path / "policy.csv"
    unsupported.write_text("text", encoding="utf-8")
    empty = tmp_path / "empty.txt"
    empty.touch()

    with pytest.raises(UnsupportedDocumentType):
        load(unsupported)
    with pytest.raises(CorpusValidationError):
        load(empty)
