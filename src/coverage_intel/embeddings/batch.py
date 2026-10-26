"""Batch embedding orchestration with retry, cache, and usage accounting."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from ..errors import EmbeddingError
from .encoder import Embedder
from .tokens import count_embedding_tokens


@dataclass(frozen=True, slots=True)
class BatchEmbeddingResult:
    """Vectors and operational counters for one batch run."""

    vectors: list[list[float]]
    api_calls: int
    retries: int
    cache_hits: int
    input_tokens: int
    estimated_cost_usd: float


def embed_in_batches(
    embedder: Embedder,
    texts: list[str],
    *,
    batch_size: int = 100,
    max_retries: int = 3,
    backoff_seconds: float = 0.5,
    input_cost_per_million: float = 0.0,
    cache: dict[str, list[float]] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> BatchEmbeddingResult:
    """Embed texts in bounded, retryable batches while avoiding duplicates."""
    if batch_size < 1 or max_retries < 0 or backoff_seconds < 0:
        raise ValueError("batch_size must be positive and retry settings non-negative")
    if input_cost_per_million < 0:
        raise ValueError("input_cost_per_million must be non-negative")
    if any(not text.strip() for text in texts):
        raise ValueError("texts must contain only non-empty values")

    store = cache if cache is not None else {}
    vectors_by_text: dict[str, list[float]] = {}
    missing: list[str] = []
    missing_seen: set[str] = set()
    cache_hits = 0
    for text in texts:
        if text in vectors_by_text:
            cache_hits += 1
        elif text in store:
            vectors_by_text[text] = store[text]
            cache_hits += 1
        elif text in missing_seen:
            cache_hits += 1
        else:
            missing.append(text)
            missing_seen.add(text)

    api_calls = 0
    retries = 0
    for start in range(0, len(missing), batch_size):
        batch = missing[start : start + batch_size]
        for attempt in range(max_retries + 1):
            try:
                batch_vectors = embedder.embed_documents(batch)
                if len(batch_vectors) != len(batch):
                    raise EmbeddingError("embedder returned an incomplete batch")
                api_calls += 1
                break
            except EmbeddingError:
                if attempt == max_retries:
                    raise
                retries += 1
                sleep(backoff_seconds * (2**attempt))
        for text, vector in zip(batch, batch_vectors, strict=True):
            vectors_by_text[text] = vector
            store[text] = vector

    ordered = [vectors_by_text[text] for text in texts]
    input_tokens = count_embedding_tokens(texts)
    return BatchEmbeddingResult(
        vectors=ordered,
        api_calls=api_calls,
        retries=retries,
        cache_hits=cache_hits,
        input_tokens=input_tokens,
        estimated_cost_usd=input_tokens * input_cost_per_million / 1_000_000,
    )
