"""Tests for meaning-preserving extraction cleanup."""

from __future__ import annotations

from coverage_intel.ingestion.cleaning import clean
from coverage_intel.ingestion.loaders import Block


def test_clean_removes_repeated_boilerplate_and_page_numbers() -> None:
    blocks = [
        Block(text="ACME INSURANCE\nCoverage applies.\nPage 1", page=1),
        Block(text="ACME INSURANCE\nCoverage excludes flood.\nPage 2", page=2),
        Block(text="ACME INSURANCE\nCoverage requires notice.\nPage 3", page=3),
    ]

    result = clean(blocks)

    assert [block.text for block in result] == [
        "Coverage applies.",
        "Coverage excludes flood.",
        "Coverage requires notice.",
    ]


def test_clean_preserves_policy_language_and_normalizes_bullets() -> None:
    blocks = [
        Block(
            text='• Section 7.2: "Loss" means direct damage.\nThe policy does not cover flood.'
        )
    ]

    result = clean(blocks)

    assert result[0].text == (
        '- Section 7.2: "Loss" means direct damage.\n\nThe policy does not cover flood.'
    )


def test_clean_removes_repeated_draft_watermark() -> None:
    blocks = [Block(text="DRAFT\nClause one", page=1), Block(text="DRAFT\nClause two", page=2)]

    result = clean(blocks)

    assert [block.text for block in result] == ["Clause one", "Clause two"]
