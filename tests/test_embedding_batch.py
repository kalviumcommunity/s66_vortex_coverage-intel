"""Tests for batch embedding orchestration."""

from __future__ import annotations

from coverage_intel.embeddings.batch import embed_in_batches
from coverage_intel.errors import EmbeddingError


class FakeEmbedder:
    dimensions = 2

    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.calls: list[list[str]] = []

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        if self.failures:
            self.failures -= 1
            raise EmbeddingError("temporary failure")
        return [[float(index), 1.0] for index, _ in enumerate(texts)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


def test_batch_runner_retries_deduplicates_and_reconstructs_order() -> None:
    embedder = FakeEmbedder(failures=1)
    sleeps: list[float] = []

    result = embed_in_batches(
        embedder,
        ["one", "two", "one", "three"],
        batch_size=2,
        backoff_seconds=0.25,
        input_cost_per_million=0.1,
        sleep=sleeps.append,
    )

    assert result.vectors[0] == result.vectors[2]
    assert result.api_calls == 2
    assert result.retries == 1
    assert result.cache_hits == 1
    assert sleeps == [0.25]
    assert result.input_tokens > 0
    assert result.estimated_cost_usd > 0
    assert len(embedder.calls) == 3


def test_batch_runner_uses_external_cache() -> None:
    embedder = FakeEmbedder()
    cache = {"cached": [9.0, 9.0]}

    result = embed_in_batches(embedder, ["cached", "new"], cache=cache)

    assert result.vectors[0] == [9.0, 9.0]
    assert result.cache_hits == 1
    assert embedder.calls == [["new"]]
