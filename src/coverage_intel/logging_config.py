"""Structured logging (FR-19).

Log query ID, timestamp, chunk IDs, latency, and errors.
Never log question text, claim details, chunk text, policy numbers, or personal data.
"""

from __future__ import annotations

import logging
import sys

import structlog

# Fields that must never appear in a log record.
REDACTED_FIELDS = frozenset(
    {"question", "chunk_text", "text", "policy_number", "claim_details", "pii"}
)


def configure_logging(level: str = "INFO", json_format: bool = True) -> None:
    """Configure structlog with redaction applied to every record."""
    processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    processors.append(
        structlog.processors.JSONRenderer()
        if json_format
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def redact(_logger: object, _name: str, event_dict: dict) -> dict:
    """Drop any field that could contain claim or personal data."""
    return {k: v for k, v in event_dict.items() if k not in REDACTED_FIELDS}
