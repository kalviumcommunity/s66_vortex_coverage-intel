"""Validated controls for deterministic model output."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelParameters:
    """Generation parameters sent to a chat model."""

    temperature: float = 0.2
    max_tokens: int | None = None
    stop: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        if self.max_tokens is not None and self.max_tokens < 1:
            raise ValueError("max_tokens must be positive")
        if len(self.stop) > 4 or any(not value.strip() for value in self.stop):
            raise ValueError("stop must contain at most four non-empty sequences")

    @classmethod
    def from_values(
        cls,
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> ModelParameters:
        """Create validated parameters from API-friendly values."""
        return cls(temperature, max_tokens, tuple(stop or ()))
