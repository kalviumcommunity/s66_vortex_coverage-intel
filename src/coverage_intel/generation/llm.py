"""LLM client behind a provider-agnostic interface.

Structured JSON output only — prose is never regex-parsed.

Spec: specs/06-generation-and-guardrails.md · Phase: phase-01
"""

from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMClient(Protocol):
    """Provider-agnostic generation interface."""

    def generate_structured(
        self, prompt: str, schema: type[T], temperature: float
    ) -> T: ...


def get_llm() -> LLMClient:
    """Return the configured LLM provider client."""
    raise NotImplementedError("Implemented in phase-01-llm-and-prompting.md")
