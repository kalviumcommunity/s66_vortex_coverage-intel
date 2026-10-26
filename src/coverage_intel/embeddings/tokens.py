"""Token accounting helpers for embedding requests."""

from __future__ import annotations

from ..generation.tokens import TokenCounter


def count_embedding_tokens(texts: list[str], model: str = "text-embedding-3-small") -> int:
    """Count input tokens using the configured embedding model encoding."""
    counter = TokenCounter(model)
    return sum(counter.count_text(text) for text in texts)
