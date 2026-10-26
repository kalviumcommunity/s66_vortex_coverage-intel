"""Provider-agnostic chat completion client.

The first implementation uses the OpenAI-compatible Chat Completions API via
``httpx`` so the application does not depend on a provider SDK at this layer.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

import httpx
from pydantic import BaseModel

from coverage_intel.config import Settings, get_settings
from coverage_intel.errors import GenerationError

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class ChatMessage:
    """A message sent to the chat model."""

    role: str
    content: str


@dataclass(frozen=True, slots=True)
class Completion:
    """The useful parts of a provider completion response."""

    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class LLMClient(Protocol):
    """Provider-agnostic chat completion interface."""

    def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> Completion: ...


class OpenAIChatClient:
    """Minimal OpenAI Chat Completions client with typed application errors."""

    def __init__(
        self,
        settings: Settings,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        if not settings.llm_api_key:
            raise GenerationError("CI_LLM_API_KEY is required for LLM requests")
        if not settings.llm_model:
            raise GenerationError("CI_LLM_MODEL is required for LLM requests")

        base_url = settings.llm_base_url or "https://api.openai.com/v1"
        self._settings = settings
        self._client = http_client or httpx.Client(base_url=base_url.rstrip("/"))
        self._owns_client = http_client is None

    def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> Completion:
        """Send one completion request and translate provider failures."""
        payload: dict[str, Any] = {
            "model": self._settings.llm_model,
            "messages": [
                {"role": message.role, "content": message.content} for message in messages
            ],
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if stop is not None:
            payload["stop"] = list(stop)

        try:
            response = self._client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {self._settings.llm_api_key}"},
                json=payload,
                timeout=self._settings.llm_timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
            choice = body["choices"][0]
            usage = body.get("usage", {})
            content = choice["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise GenerationError(f"LLM completion failed: {exc}") from exc

        if not isinstance(content, str):
            raise GenerationError("LLM completion returned non-text content")

        return Completion(
            content=content,
            model=str(body.get("model", self._settings.llm_model)),
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            total_tokens=int(usage.get("total_tokens", 0)),
        )

    def close(self) -> None:
        """Close the underlying HTTP client when this instance owns it."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OpenAIChatClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def get_llm(settings: Settings | None = None) -> LLMClient:
    """Build the configured LLM provider client."""
    return OpenAIChatClient(settings or get_settings())
