"""Enterprise Exception Hierarchy for RAG pipeline operations.

All domain exceptions inherit from RagBaseException and provide structured error codes
and HTTP-compatible status mappings.
"""

from __future__ import annotations


class RagBaseException(Exception):
    """Base exception for all RAG pipeline domain errors."""

    def __init__(self, message: str, error_code: str = "RAG_ERROR", retryable: bool = False) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.retryable = retryable

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class ConfigurationError(RagBaseException):
    """Raised when critical environment variables or runtime configurations fail validation."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="CONFIG_VALIDATION_ERROR", retryable=False)


class PineconeConnectionError(RagBaseException):
    """Raised when initial handshake or connection to Pinecone Vector DB fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="PINECONE_CONNECTION_ERROR", retryable=True)


class VectorRepositoryError(RagBaseException):
    """Raised when querying, upserting, or managing Pinecone index vectors encounters errors."""

    def __init__(self, message: str, retryable: bool = False) -> None:
        super().__init__(message, error_code="VECTOR_REPOSITORY_ERROR", retryable=retryable)


class EmbeddingInferenceError(RagBaseException):
    """Raised when Pinecone's hosted inference API fails to generate embeddings."""

    def __init__(self, message: str, retryable: bool = True) -> None:
        super().__init__(message, error_code="EMBEDDING_INFERENCE_ERROR", retryable=retryable)


class GrokServiceError(RagBaseException):
    """Raised when communicating with the xAI Grok API fails or returns an invalid payload."""

    def __init__(self, message: str, retryable: bool = True) -> None:
        super().__init__(message, error_code="GROK_API_ERROR", retryable=retryable)


class ContextCompilationError(RagBaseException):
    """Raised when preparing or compiling retrieved chunks exceeds context budgets or boundaries."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="CONTEXT_COMPILATION_ERROR", retryable=False)

