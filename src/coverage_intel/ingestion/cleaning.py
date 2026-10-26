"""Boilerplate removal and normalisation — FR-03.

Removes page headers/footers, standalone page numbers, and watermarks.
Preserves clause references, defined terms, negation, and amounts.

Spec: specs/04-ingestion.md
"""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict

from .loaders import Block

PAGE_NUMBER = re.compile(r"^\s*(?:page\s+)?\d+(?:\s+of\s+\d+)?\s*$", re.IGNORECASE)
BULLETS = str.maketrans({"•": "-", "▪": "-", "‣": "-", "◦": "-"})


def clean(blocks: list[Block]) -> list[Block]:
    """Clean extracted blocks without losing coverage-meaningful content."""
    boilerplate = _repeated_lines(blocks)
    cleaned: list[Block] = []
    for block in blocks:
        lines = []
        for raw_line in unicodedata.normalize("NFKC", block.text).translate(BULLETS).splitlines():
            line = re.sub(r"[ \t]+", " ", raw_line).strip()
            if not line or PAGE_NUMBER.fullmatch(line) or line in boilerplate:
                continue
            if line.casefold() == "draft" or line.casefold().startswith("draft "):
                continue
            lines.append(line)
        text = "\n\n".join(lines).strip()
        if text:
            cleaned.append(block.model_copy(update={"text": text}))
    return cleaned


def _repeated_lines(blocks: list[Block]) -> set[str]:
    """Find exact lines repeated across at least 60% of known pages."""
    pages = {block.page for block in blocks if block.page is not None}
    if len(pages) < 2:
        return set()
    required = max(2, (len(pages) * 6 + 9) // 10)
    page_hits: defaultdict[str, set[int]] = defaultdict(set)
    for block in blocks:
        if block.page is None:
            continue
        for line in unicodedata.normalize("NFKC", block.text).splitlines():
            normalized = re.sub(r"[ \t]+", " ", line).strip()
            if normalized:
                page_hits[normalized].add(block.page)
    return {line for line, hit_pages in page_hits.items() if len(hit_pages) >= required}
