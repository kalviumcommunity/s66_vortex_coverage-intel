"""Section-aware, token-aware chunking — FR-04.

Defaults: 500 tokens, 50-token overlap, both configurable.
Invariants C-1..C-5 in specs/04-ingestion.md.

Spec: specs/04-ingestion.md
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import tiktoken

from .loaders import Block
from .metadata import Chunk, SourceCategory


@dataclass(frozen=True, slots=True)
class TokenChunkingConfig:
    """Tokenizer-aware chunk window configuration."""

    size: int = 500
    overlap: int = 50
    model: str = "gpt-4o-mini"

    def __post_init__(self) -> None:
        if self.size < 1 or self.overlap < 0 or self.overlap >= self.size:
            raise ValueError("size must be positive and overlap must be less than size")


def _encoding(model: str) -> tiktoken.Encoding:
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def chunk(
    blocks: list[Block],
    size: int = 500,
    overlap: int = 50,
    *,
    document_id: str = "unknown-document",
    category: SourceCategory = SourceCategory.APPROVED_REFERENCE,
    model: str = "gpt-4o-mini",
) -> list[Chunk]:
    """Split blocks into retrieval units respecting section boundaries."""
    config = TokenChunkingConfig(size=size, overlap=overlap, model=model)
    encoding = _encoding(config.model)

    groups: dict[str, list[Block]] = {}
    for block in blocks:
        if block.text.strip():
            groups.setdefault(block.section or "Unsectioned", []).append(block)

    result: list[Chunk] = []
    step = config.size - config.overlap
    for section, section_blocks in groups.items():
        token_ids: list[int] = []
        token_pages: list[int | None] = []
        for block in section_blocks:
            ids = encoding.encode(block.text)
            token_ids.extend(ids)
            token_pages.extend([block.page] * len(ids))
        for start in range(0, len(token_ids), step):
            window = token_ids[start : start + config.size]
            if not window:
                continue
            text = encoding.decode(window).strip()
            if not text:
                continue
            pages = [
                page for page in token_pages[start : start + config.size] if page is not None
            ]
            source_blocks = section_blocks_for_window(
                section_blocks, start, config.size, encoding
            )
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
            if start + config.size >= len(token_ids):
                break
    return result


def section_blocks_for_window(
    blocks: list[Block], start: int, size: int, encoding: tiktoken.Encoding
) -> list[Block]:
    """Approximate the source blocks touched by a token window."""
    cursor = 0
    touched: list[Block] = []
    for block in blocks:
        block_size = len(encoding.encode(block.text))
        if cursor + block_size > start and cursor < start + size:
            touched.append(block)
        cursor += block_size
    return touched or blocks[:1]
