"""FastAPI Dependency Injection providers — Settings, VectorStore, and Security."""

from __future__ import annotations

from typing import Annotated

from fastapi import Header

from ..config import Settings, get_settings
from ..embeddings.encoder import Embedder, get_embedder
from ..vectorstore.index import VectorStore, get_vector_store
from .security import verify_access_key


def get_api_settings() -> Settings:
    """Provide the active runtime settings singleton."""
    return get_settings()


def get_active_vector_store() -> VectorStore:
    """Provide the active vector store singleton."""
    return get_vector_store()


def get_active_embedder() -> Embedder:
    """Provide the active embedding encoder."""
    return get_embedder()


def require_upload_access(
    x_upload_access_key: Annotated[str | None, Header(alias="X-Upload-Access-Key")] = None,
) -> None:
    """Enforce upload access key authentication."""
    verify_access_key(x_upload_access_key)

