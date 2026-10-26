"""Token counting and cost estimation for chat requests."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import tiktoken

from coverage_intel.generation.llm import ChatMessage


@dataclass(frozen=True, slots=True)
class CostEstimate:
    """Token usage and estimated USD cost for one request."""

    prompt_tokens: int
    completion_tokens: int
    input_cost_usd: float
    output_cost_usd: float

    @property
    def total_tokens(self) -> int:
        """Return prompt plus completion tokens."""
        return self.prompt_tokens + self.completion_tokens

    @property
    def total_cost_usd(self) -> float:
        """Return the combined estimated cost."""
        return self.input_cost_usd + self.output_cost_usd


class TokenCounter:
    """Count tokens using the encoding associated with a model when available."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        try:
            self._encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self._encoding = tiktoken.get_encoding("cl100k_base")

    def count_text(self, text: str) -> int:
        """Count encoded tokens in text."""
        return len(self._encoding.encode(text))

    def count_messages(self, messages: Sequence[ChatMessage]) -> int:
        """Count content plus a small Chat Completions message envelope."""
        # The envelope is an estimate because exact overhead can vary by model.
        message_tokens = sum(
            self.count_text(message.role) + self.count_text(message.content) + 4
            for message in messages
        )
        return message_tokens + 2

    def estimate_cost(
        self,
        messages: Sequence[ChatMessage],
        completion_tokens: int,
        *,
        input_cost_per_million: float,
        output_cost_per_million: float,
    ) -> CostEstimate:
        """Estimate USD cost from token counts and published unit prices."""
        if completion_tokens < 0:
            raise ValueError("completion_tokens must be non-negative")
        if input_cost_per_million < 0 or output_cost_per_million < 0:
            raise ValueError("cost rates must be non-negative")

        prompt_tokens = self.count_messages(messages)
        input_cost = prompt_tokens * input_cost_per_million / 1_000_000
        output_cost = completion_tokens * output_cost_per_million / 1_000_000
        return CostEstimate(prompt_tokens, completion_tokens, input_cost, output_cost)
