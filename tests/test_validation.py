"""Tests for corpus-wide ingestion validation."""

from __future__ import annotations

from pathlib import Path

from coverage_intel.ingestion.validation import prepare_corpus


def test_prepare_corpus_reports_completeness_and_failures(tmp_path: Path) -> None:
    valid = tmp_path / "valid.txt"
    valid.write_text("COVERAGE\nThe policy covers fire.", encoding="utf-8")
    unsupported = tmp_path / "bad.csv"
    unsupported.write_text("not an approved source", encoding="utf-8")

    documents, report = prepare_corpus([valid, unsupported], target_success_rate=0.5)

    assert len(documents) == 1
    assert report.total == 2
    assert report.indexed == 1
    assert report.failed == 1
    assert report.meets_target is True
    assert report.failures[0].code == "UnsupportedDocumentType"


def test_empty_corpus_does_not_claim_success(tmp_path: Path) -> None:
    _, report = prepare_corpus([], target_success_rate=0.0)

    assert report.success_rate == 0.0
    assert report.meets_target is False
