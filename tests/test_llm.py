"""Unit tests for the first LLM completion call."""

from __future__ import annotations

import httpx
import pytest

from coverage_intel.config import Settings
from coverage_intel.errors import GenerationError
from coverage_intel.generation.llm import ChatMessage, OpenAIChatClient


def _settings() -> Settings:
    return Settings(llm_api_key="test-key", llm_model="test-model")


def test_complete_returns_text_and_usage() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-key"
        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "choices": [{"message": {"content": "Coverage depends on the endorsement."}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20},
            },
        )

    transport = httpx.MockTransport(handler)
    with OpenAIChatClient(
        _settings(), http_client=httpx.Client(transport=transport, base_url="https://test.local/v1")
    ) as client:
        result = client.complete([ChatMessage("user", "What does the policy say?")])

    assert result.content == "Coverage depends on the endorsement."
    assert result.total_tokens == 20


def test_provider_error_becomes_generation_error() -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(429, json={"error": "rate limited"}))
    with (
        OpenAIChatClient(
            _settings(),
            http_client=httpx.Client(transport=transport, base_url="https://test.local/v1"),
        ) as client,
        pytest.raises(GenerationError, match="LLM completion failed"),
    ):
        client.complete([ChatMessage("user", "Try again")])


def test_missing_api_key_fails_before_network_call() -> None:
    with pytest.raises(GenerationError, match="CI_LLM_API_KEY"):
        OpenAIChatClient(Settings(llm_api_key="", llm_model="test-model"))
