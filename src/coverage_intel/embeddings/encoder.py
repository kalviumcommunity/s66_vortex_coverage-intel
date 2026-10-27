"""Embedding encoder behind a provider-agnostic interface — FR-06.

Documents and queries **must** use the same model. A dimension change requires
a full re-index and threshold recalibration.

Spec: specs/05-retrieval.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

import httpx

from ..config import Settings, get_settings
from ..errors import EmbeddingError


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    """Validated numeric representation of one text input."""

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise ValueError("embedding vectors must contain at least one value")
        if any(not math.isfinite(value) for value in self.values):
            raise ValueError("embedding values must be finite")

    @property
    def dimensions(self) -> int:
        """Return the vector dimensionality."""
        return len(self.values)

    @property
    def norm(self) -> float:
        """Return the Euclidean length."""
        return math.sqrt(sum(value * value for value in self.values))

    def normalized(self) -> EmbeddingVector:
        """Return a unit-length copy, rejecting a zero vector."""
        length = self.norm
        if length == 0.0:
            raise ValueError("zero vectors cannot be normalized")
        return EmbeddingVector(tuple(value / length for value in self.values))


def validate_batch(vectors: list[EmbeddingVector]) -> int:
    """Validate that a batch uses one consistent dimensionality."""
    if not vectors:
        raise ValueError("embedding batch must not be empty")
    dimensions = vectors[0].dimensions
    if any(vector.dimensions != dimensions for vector in vectors[1:]):
        raise ValueError("all embedding vectors must have the same dimensionality")
    return dimensions


class Embedder(Protocol):
    """Provider-agnostic embedding interface."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...

    @property
    def dimensions(self) -> int: ...


class OpenAIEmbeddingClient:
    """OpenAI-compatible embeddings client with consistent vector dimensions."""

    def __init__(
        self,
        settings: Settings,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        if not settings.embedding_api_key:
            raise EmbeddingError("CI_EMBEDDING_API_KEY is required for embedding requests")
        if not settings.embedding_model:
            raise EmbeddingError("CI_EMBEDDING_MODEL is required for embedding requests")
        base_url = settings.embedding_base_url or "https://api.openai.com/v1"
        self._settings = settings
        self._client = http_client or httpx.Client(base_url=base_url.rstrip("/"))
        self._owns_client = http_client is None
        self._dimensions: int | None = None

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a non-empty batch and preserve provider input order."""
        if not texts or any(not text.strip() for text in texts):
            raise EmbeddingError("embedding input must contain non-empty text")
        try:
            response = self._client.post(
                "/embeddings",
                headers={"Authorization": f"Bearer {self._settings.embedding_api_key}"},
                json={"model": self._settings.embedding_model, "input": texts},
                timeout=self._settings.llm_timeout_seconds,
            )
            response.raise_for_status()
            entries = sorted(response.json()["data"], key=lambda item: item["index"])
            vectors = [list(map(float, entry["embedding"])) for entry in entries]
            validate_batch([EmbeddingVector(tuple(vector)) for vector in vectors])
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise EmbeddingError(f"Embedding request failed: {exc}") from exc
        if len(vectors) != len(texts):
            raise EmbeddingError("embedding provider returned an incomplete batch")
        dimensions = len(vectors[0])
        if self._dimensions is not None and dimensions != self._dimensions:
            raise EmbeddingError("embedding dimensions changed during client lifetime")
        self._dimensions = dimensions
        return vectors

    def embed_query(self, text: str) -> list[float]:
        """Embed one query using the same configured model as documents."""
        return self.embed_documents([text])[0]

    @property
    def dimensions(self) -> int:
        """Return dimensions discovered from the first successful response."""
        if self._dimensions is None:
            raise EmbeddingError("embedding dimensions are unknown before the first request")
        return self._dimensions

    def close(self) -> None:
        """Close the underlying HTTP client when owned by this instance."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OpenAIEmbeddingClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class DeterministicEmbedder:
    """Deterministic offline embedder for tests, local execution, and fallback."""

    def __init__(self, dimensions: int = 1536) -> None:
        self._dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts or any(not text.strip() for text in texts):
            raise EmbeddingError("embedding input must contain non-empty text")
        return [self.embed_query(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        import hashlib

        vec = [0.0] * self._dimensions
        words = text.lower().split()
        if not words:
            vec[0] = 1.0
            return vec
        for word in words:
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self._dimensions
            sign = 1.0 if ((h >> 16) & 1) else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0.0:
            vec[0] = 1.0
            return vec
        return [v / norm for v in vec]

    @property
    def dimensions(self) -> int:
        return self._dimensions


def get_embedder(settings: Settings | None = None) -> Embedder:
    """Return the configured embedding provider or deterministic fallback."""
    cfg = settings or get_settings()
    if cfg.embedding_api_key and cfg.embedding_model and cfg.embedding_model != "local":
        return OpenAIEmbeddingClient(cfg)
    return DeterministicEmbedder()
