"""Tests for API-backed embedding generation."""

from __future__ import annotations

import httpx
import pytest

from coverage_intel.config import Settings
from coverage_intel.embeddings.encoder import OpenAIEmbeddingClient
from coverage_intel.errors import EmbeddingError


def _settings() -> Settings:
    return Settings(embedding_api_key="test-key", embedding_model="test-embedding")


def test_embed_documents_orders_vectors_and_records_dimensions() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/embeddings"
        assert request.headers["Authorization"] == "Bearer test-key"
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": 1, "embedding": [0.3, 0.4]},
                    {"index": 0, "embedding": [0.1, 0.2]},
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://test.local/v1")
    with OpenAIEmbeddingClient(_settings(), http_client=client) as embedder:
        vectors = embedder.embed_documents(["first", "second"])
        assert embedder.dimensions == 2

    assert vectors == [[0.1, 0.2], [0.3, 0.4]]


def test_empty_input_and_provider_failures_are_typed() -> None:
    with pytest.raises(EmbeddingError, match="non-empty"):
        OpenAIEmbeddingClient(_settings()).embed_documents([])

    client = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(500)),
        base_url="https://test.local/v1",
    )
    with (
        OpenAIEmbeddingClient(_settings(), http_client=client) as embedder,
        pytest.raises(EmbeddingError, match="Embedding request failed"),
    ):
        embedder.embed_query("question")
