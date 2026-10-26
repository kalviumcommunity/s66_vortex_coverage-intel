"""Section-aware, token-aware chunking — FR-04.

Defaults: 500 tokens, 50-token overlap, both configurable.
Invariants C-1..C-5 in specs/04-ingestion.md.

Spec: specs/04-ingestion.md
"""

from __future__ import annotations

import hashlib

import tiktoken

from .loaders import Block
from .metadata import Chunk, SourceCategory

_ENCODING = tiktoken.get_encoding("cl100k_base")


def chunk(
    blocks: list[Block],
    size: int = 500,
    overlap: int = 50,
    *,
    document_id: str = "unknown-document",
    category: SourceCategory = SourceCategory.APPROVED_REFERENCE,
) -> list[Chunk]:
    """Split blocks into retrieval units respecting section boundaries."""
    if size < 1 or overlap < 0 or overlap >= size:
        raise ValueError("size must be positive and overlap must be less than size")

    groups: dict[str, list[Block]] = {}
    for block in blocks:
        if block.text.strip():
            groups.setdefault(block.section or "Unsectioned", []).append(block)

    result: list[Chunk] = []
    step = size - overlap
    for section, section_blocks in groups.items():
        token_ids: list[int] = []
        token_pages: list[int | None] = []
        for block in section_blocks:
            ids = _ENCODING.encode(block.text)
            token_ids.extend(ids)
            token_pages.extend([block.page] * len(ids))
        for start in range(0, len(token_ids), step):
            window = token_ids[start : start + size]
            if not window:
                continue
            text = _ENCODING.decode(window).strip()
            if not text:
                continue
            pages = [page for page in token_pages[start : start + size] if page is not None]
            source_blocks = section_blocks_for_window(section_blocks, start, size)
            char_start = next(
                (block.char_start for block in source_blocks if block.char_start is not None), None
            )
            char_end = next(
                (block.char_end for block in reversed(source_blocks) if block.char_end is not None),
                None,
            )
            page = min(pages) if pages else None
            page_end = max(pages) if pages else None
            chunk_key = f"{document_id}:{section}:{start}:{text}"
            chunk_id = hashlib.sha256(chunk_key.encode()).hexdigest()[:16]
            result.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    text=text,
                    section=section,
                    page=page,
                    page_end=page_end,
                    token_count=len(window),
                    char_start=char_start,
                    char_end=char_end,
                    category=category,
                )
            )
            if start + size >= len(token_ids):
                break
    return result


def section_blocks_for_window(blocks: list[Block], start: int, size: int) -> list[Block]:
    """Approximate the source blocks touched by a token window."""
    cursor = 0
    touched: list[Block] = []
    for block in blocks:
        block_size = len(_ENCODING.encode(block.text))
        if cursor + block_size > start and cursor < start + size:
            touched.append(block)
        cursor += block_size
    return touched or blocks[:1]
