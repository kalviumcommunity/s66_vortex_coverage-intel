"""Tests for embedding quality sanity checks."""

from __future__ import annotations

import pytest

from coverage_intel.embeddings.quality import check_quality


class FakeEmbedder:
    dimensions = 3


def test_quality_report_detects_duplicates_zeroes_and_dimensions() -> None:
    report = check_quality(
        FakeEmbedder(),
        [[1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [1.0, 0.0]],
    )

    assert report["count"] == 4
    assert report["dimension_mismatches"] == [3]
    assert report["zero_vectors"] == [2]
    assert report["near_duplicate_pairs"] == [(0, 1)]
    assert report["healthy"] is False


def test_quality_report_accepts_varied_valid_vectors() -> None:
    report = check_quality(FakeEmbedder(), [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    assert report["healthy"] is True
    assert all(value >= 0.0 for value in report["variance"])


def test_quality_threshold_is_validated() -> None:
    with pytest.raises(ValueError, match="duplicate_threshold"):
        check_quality(FakeEmbedder(), [[1.0, 0.0, 0.0]], duplicate_threshold=1.1)
