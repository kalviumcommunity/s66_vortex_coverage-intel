"""Tests for token counting and cost estimation."""

from __future__ import annotations

import pytest

from coverage_intel.generation.llm import ChatMessage
from coverage_intel.generation.tokens import TokenCounter


def test_token_counter_counts_text_and_message_envelope() -> None:
    counter = TokenCounter("test-model-not-known")
    text_tokens = counter.count_text("The policy excludes flood damage.")
    message_tokens = counter.count_messages(
        [ChatMessage("user", "The policy excludes flood damage.")]
    )

    assert text_tokens > 0
    assert message_tokens >= text_tokens + counter.count_text("user") + 6


def test_cost_estimate_uses_separate_input_and_output_rates() -> None:
    counter = TokenCounter()
    estimate = counter.estimate_cost(
        [ChatMessage("user", "What is covered?")],
        completion_tokens=100,
        input_cost_per_million=0.15,
        output_cost_per_million=0.60,
    )

    assert estimate.total_tokens == estimate.prompt_tokens + 100
    assert estimate.input_cost_usd == pytest.approx(estimate.prompt_tokens * 0.15 / 1_000_000)
    assert estimate.output_cost_usd == pytest.approx(0.60 / 10_000)


def test_negative_usage_or_rates_are_rejected() -> None:
    counter = TokenCounter()
    with pytest.raises(ValueError):
        counter.estimate_cost([], -1, input_cost_per_million=0.15, output_cost_per_million=0.60)
    with pytest.raises(ValueError):
        counter.estimate_cost([], 1, input_cost_per_million=-0.15, output_cost_per_million=0.60)
