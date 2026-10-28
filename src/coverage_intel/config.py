"""Central configuration. Every tunable lives here — never at a call site.

See docs/DEPLOYMENT.md §3 for the environment variable reference.
"""

from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Runtime settings, loaded from environment variables prefixed ``CI_``."""

    model_config = SettingsConfigDict(env_prefix="CI_", env_file=".env", extra="ignore")

    # ── Models ───────────────────────────────────────────────
    llm_model: str = os.getenv("XAI_GROK_MODEL", "gpt-4o-mini")
    embedding_model: str = os.getenv("PINECONE_EMBED_MODEL", "multilingual-e5-large")
    llm_base_url: str | None = os.getenv("XAI_GROK_BASE_URL", None)
    embedding_base_url: str | None = None
    rerank_model: str | None = None

    llm_api_key: str = os.getenv("XAI_GROK_API_KEY", "")
    llm_timeout_seconds: float = 30.0
    embedding_api_key: str = os.getenv("PINECONE_API_KEY", "")
    upload_access_key: str = ""

    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "")

    # ── Ingestion (FR-04) ────────────────────────────────────
    chunk_size_tokens: int = 500
    chunk_overlap_tokens: int = 50
    corpus_dir: str = "data/corpus"

    # ── Retrieval (FR-08, FR-09, FR-14) ─────────────────────
    top_k: int = 5
    hybrid_alpha: float = 0.7
    similarity_threshold: float = 0.35
    relevance_floor: float = 0.30
    rerank_enabled: bool = False
    rerank_top_n: int = 20

    # ── Generation (FR-11, FR-12) ───────────────────────────
    generation_temperature: float = 0.2
    max_context_tokens: int = 6000

    # ── Storage & ops ───────────────────────────────────────
    vector_store: str = "pinecone" if os.getenv("PINECONE_INDEX_NAME") else "chroma"
    qdrant_url: str | None = None
    log_level: str = "INFO"
    log_format: str = "json"

    # ── API ─────────────────────────────────────────────────
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    max_upload_mb: int = 25

    @model_validator(mode="after")
    def _validate(self) -> Settings:
        """Enforce the invariants that must never be violated at runtime."""
        if self.chunk_overlap_tokens >= self.chunk_size_tokens:
            raise ValueError("CI_CHUNK_OVERLAP_TOKENS must be < CI_CHUNK_SIZE_TOKENS")
        if self.generation_temperature > 0.2:
            raise ValueError("CI_GENERATION_TEMPERATURE must be <= 0.2 (FR-12)")
        if not 0.0 <= self.hybrid_alpha <= 1.0:
            raise ValueError("CI_HYBRID_ALPHA must be between 0.0 and 1.0")
        if not 1 <= self.top_k <= 20:
            raise ValueError("CI_TOP_K must be between 1 and 20")
        if self.similarity_threshold < 0 or self.relevance_floor < 0:
            raise ValueError("similarity and relevance thresholds must be non-negative")
        if self.max_context_tokens < 1 or self.rerank_top_n < 1:
            raise ValueError("context and rerank limits must be positive")
        if not 1 <= self.api_port <= 65535:
            raise ValueError("CI_API_PORT must be a valid TCP port")
        return self


def get_settings() -> Settings:
    """Return cached settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


_settings: Settings | None = None
