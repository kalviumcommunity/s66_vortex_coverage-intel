"""Tests for schema-validated JSON model output."""

from __future__ import annotations

import httpx
import pytest
from pydantic import BaseModel

from coverage_intel.config import Settings
from coverage_intel.errors import GenerationError
from coverage_intel.generation.llm import ChatMessage, OpenAIChatClient


class CoverageDecision(BaseModel):
    covered: bool
    reason: str


def _client(content: str) -> OpenAIChatClient:
    def handler(request: httpx.Request) -> httpx.Response:
        body = request.read()
        assert b"response_format" in body
        return httpx.Response(
            200, json={"model": "test", "choices": [{"message": {"content": content}}]}
        )

    return OpenAIChatClient(
        Settings(llm_api_key="test-key", llm_model="test-model"),
        http_client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://test.local/v1"),
    )


def test_structured_output_is_parsed_and_validated() -> None:
    with _client('{"covered": true, "reason": "The endorsement applies."}') as client:
        result = client.generate_structured(
            [ChatMessage("user", "Is it covered?")], CoverageDecision
        )

    assert result.covered is True
    assert result.reason.startswith("The endorsement")


@pytest.mark.parametrize("content", ["not-json", '{"covered": "maybe"}'])
def test_invalid_structured_output_becomes_generation_error(content: str) -> None:
    with (
        _client(content) as client,
        pytest.raises(GenerationError, match="Structured LLM output"),
    ):
        client.generate_structured([ChatMessage("user", "Question")], CoverageDecision)
