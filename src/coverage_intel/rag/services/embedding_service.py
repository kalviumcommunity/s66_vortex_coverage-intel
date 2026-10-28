"""Embedding Service — native Pinecone hosted inference API client.

Utilizes pc.inference.embed natively with production models such as multilingual-e5-large.
Does not use OpenAI or third-party embedding models.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from pinecone import Pinecone

from ..exceptions import EmbeddingInferenceError

logger = logging.getLogger("coverage-intel.rag.embeddings")


class EmbeddingService:
    """Service handling text embedding generation via Pinecone's native hosted inference API."""

    def __init__(
        self,
        pinecone_client: Pinecone,
        model: str = "multilingual-e5-large",
    ) -> None:
        """Initialize the EmbeddingService with an injected Pinecone client instance.

        Args:
            pinecone_client: Instantiated Pinecone connection.
            model: Target hosted inference embedding model name (e.g. multilingual-e5-large).
        """
        self._client = pinecone_client
        self._model = model

    @property
    def model_name(self) -> str:
        """Return the active inference embedding model name."""
        return self._model

    def embed_texts(
        self,
        texts: Sequence[str],
        input_type: str = "passage",
        truncate: str = "END",
    ) -> list[list[float]]:
        """Generate dense vector embeddings for a batch of text passages.

        Args:
            texts: List of non-empty strings to embed.
            input_type: Inference parameter ('passage' for documents, 'query' for search queries).
            truncate: Truncation strategy ('END' or 'NONE').

        Returns:
            List of float vector lists matching the input order.

        Raises:
            EmbeddingInferenceError: If Pinecone's inference API encounters an error.
        """
        if not texts:
            return []

        cleaned_texts = [t.strip() for t in texts]
        if any(not t for t in cleaned_texts):
            raise EmbeddingInferenceError("Embedding input must contain non-empty text strings.", retryable=False)

        try:
            logger.debug(
                "Requesting Pinecone inference embeddings for %d inputs using model '%s' (input_type=%s)",
                len(cleaned_texts),
                self._model,
                input_type,
            )
            response: Any = self._client.inference.embed(
                model=self._model,
                inputs=cleaned_texts,
                parameters={
                    "input_type": input_type,
                    "truncate": truncate,
                },
            )

            # Pinecone inference returns an EmbeddingsList containing items with .values or ['values']
            vectors: list[list[float]] = []
            for item in response:
                if hasattr(item, "values"):
                    vectors.append(list(map(float, item.values)))
                elif isinstance(item, dict) and "values" in item:
                    vectors.append(list(map(float, item["values"])))
                else:
                    raise EmbeddingInferenceError(
                        f"Unexpected item structure from Pinecone inference response: {type(item)}"
                    )

            if len(vectors) != len(cleaned_texts):
                raise EmbeddingInferenceError(
                    f"Pinecone inference returned {len(vectors)} vectors for {len(cleaned_texts)} inputs."
                )

            return vectors

        except EmbeddingInferenceError:
            raise
        except Exception as exc:
            logger.error("Pinecone hosted inference embedding failed: %s", exc, exc_info=True)
            raise EmbeddingInferenceError(
                f"Failed to generate embeddings via Pinecone inference ({self._model}): {exc}",
                retryable=True,
            ) from exc

    def embed_query(self, query: str) -> list[float]:
        """Generate an asymmetric query embedding for similarity search.

        Args:
            query: The user search or coverage question.

        Returns:
            A single float vector list.
        """
        if not query or not query.strip():
            raise EmbeddingInferenceError("Query string cannot be empty.", retryable=False)

        # For e5 models, input_type="query" applies asymmetric query weighting
        vectors = self.embed_texts([query.strip()], input_type="query")
        return vectors[0]

