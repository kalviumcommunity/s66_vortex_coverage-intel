"""Configuration Layer — Safe runtime validation for xAI Grok and Pinecone.

Validates required credentials (XAI_GROK_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME)
and provides typed defaults for the enterprise RAG stack.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ConfigurationError


class RagSettings(BaseSettings):
    """Production runtime settings for Pinecone Inference and xAI Grok LLM."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # ── Pinecone Credentials & Parameters ─────────────────────────────────────
    pinecone_api_key: str = Field(
        default="",
        alias="PINECONE_API_KEY",
        description="Pinecone Vector Database API Key",
    )
    pinecone_index_name: str = Field(
        default="",
        alias="PINECONE_INDEX_NAME",
        description="Target Pinecone Index name for vector storage",
    )
    pinecone_embed_model: str = Field(
        default="multilingual-e5-large",
        alias="PINECONE_EMBED_MODEL",
        description="Hosted inference embedding model (Pinecone native)",
    )

    # ── xAI Grok Credentials & Parameters ─────────────────────────────────────
    xai_grok_api_key: str = Field(
        default="",
        alias="XAI_GROK_API_KEY",
        description="xAI Grok API key for generation",
    )
    xai_grok_base_url: str = Field(
        default="https://api.x.ai/v1",
        alias="XAI_GROK_BASE_URL",
        description="xAI Grok base URL for OpenAI-compatible SDK calls",
    )
    xai_grok_model: str = Field(
        default="grok-2-latest",
        alias="XAI_GROK_MODEL",
        description="xAI Grok model identifier (e.g. grok-2-latest, grok-beta)",
    )

    # ── RAG Pipeline Parameters ───────────────────────────────────────────────
    top_k: int = Field(default=5, ge=1, le=50, description="Top-k retrieval limit")
    similarity_threshold: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Minimum cosine similarity required for evidence relevance",
    )
    max_context_tokens: int = Field(
        default=4000,
        ge=256,
        description="Maximum token budget for compiling retrieved context",
    )
    generation_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for strict factual grounding",
    )
    network_timeout_seconds: float = Field(
        default=30.0,
        ge=1.0,
        description="Timeout for external API calls in seconds",
    )

    @model_validator(mode="after")
    def validate_required_credentials(self) -> Self:
        """Enforce presence of critical credentials when running in production."""
        # Support fallback from alternative env names
        if not self.xai_grok_api_key:
            self.xai_grok_api_key = os.getenv("XAI_API_KEY", "")

        return self

    def assert_credentials_present(self) -> None:
        """Explicitly verify that all production credentials exist before making remote calls."""
        missing = []
        if not self.pinecone_api_key:
            missing.append("PINECONE_API_KEY")
        if not self.pinecone_index_name:
            missing.append("PINECONE_INDEX_NAME")
        if not self.xai_grok_api_key:
            missing.append("XAI_GROK_API_KEY")

        if missing:
            raise ConfigurationError(
                f"Missing required enterprise RAG environment variables: {', '.join(missing)}. "
                "Please configure them in your environment or .env file."
            )


@lru_cache(maxsize=1)
def get_rag_settings() -> RagSettings:
    """Return a cached singleton instance of RagSettings."""
    return RagSettings()

