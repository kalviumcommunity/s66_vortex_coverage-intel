"""Typed errors. Retrieval, generation, and refusal are distinct outcomes.

A guardrail refusal is NOT an error — it is a correct product response (HTTP 200).
"""

from __future__ import annotations


class CoverageIntelError(Exception):
    """Base class for all application errors."""

    http_status: int = 500
    error_code: str = "InternalError"
    retryable: bool = False


class RetrievalError(CoverageIntelError):
    """Vector store or keyword index unavailable."""

    http_status = 503
    error_code = "RetrievalError"
    retryable = True


class GenerationError(CoverageIntelError):
    """LLM provider failed or returned unparseable structured output."""

    http_status = 502
    error_code = "GenerationError"
    retryable = True


class UnsupportedDocumentType(CoverageIntelError):
    """File is not PDF, DOCX, or TXT."""

    http_status = 415
    error_code = "UnsupportedDocumentType"


class CorpusValidationError(CoverageIntelError):
    """Document is missing required traceability metadata."""

    http_status = 422
    error_code = "CorpusValidationError"


class UnauthorizedUpload(CoverageIntelError):
    """Missing or invalid upload access key (FR-16)."""

    http_status = 401
    error_code = "UnauthorizedUpload"


class ExtractionError(CoverageIntelError):
    """Text extraction produced nothing usable — e.g. a scanned PDF.

    OCR is out of MVP scope; this fails loudly rather than indexing noise.
    """

    http_status = 422
    error_code = "ExtractionError"
