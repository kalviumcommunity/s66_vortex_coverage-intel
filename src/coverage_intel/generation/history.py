"""Token-bounded conversation history management."""

from __future__ import annotations

from collections.abc import Sequence

from coverage_intel.generation.llm import ChatMessage
from coverage_intel.generation.tokens import TokenCounter


class MessageHistory:
    """Maintain a system prompt and trim old user/assistant turns by token budget."""

    def __init__(self, system_prompt: str, *, counter: TokenCounter | None = None) -> None:
        if not system_prompt.strip():
            raise ValueError("system_prompt must not be empty")
        self._system = ChatMessage("system", system_prompt)
        self._messages: list[ChatMessage] = []
        self._counter = counter or TokenCounter()

    @property
    def messages(self) -> tuple[ChatMessage, ...]:
        """Return the current system prompt and conversation messages."""
        return (self._system, *self._messages)

    def add(self, role: str, content: str) -> None:
        """Append a user or assistant message."""
        if role not in {"user", "assistant"}:
            raise ValueError("conversation role must be user or assistant")
        if not content.strip():
            raise ValueError("message content must not be empty")
        self._messages.append(ChatMessage(role, content))

    def token_count(self, messages: Sequence[ChatMessage] | None = None) -> int:
        """Count tokens for the supplied messages or current history."""
        return self._counter.count_messages(messages or self.messages)

    def trim_to_budget(
        self, max_tokens: int, *, reserve_tokens: int = 0
    ) -> tuple[ChatMessage, ...]:
        """Keep the newest complete turns within the available context budget."""
        if max_tokens <= 0 or reserve_tokens < 0 or reserve_tokens >= max_tokens:
            raise ValueError("max_tokens must be positive and exceed reserve_tokens")

        budget = max_tokens - reserve_tokens
        kept: list[ChatMessage] = []
        turns = self._turns()
        for turn in reversed(turns):
            candidate = [self._system, *turn, *kept]
            if self.token_count(candidate) > budget:
                break
            kept = [*turn, *kept]

        result = (self._system, *kept)
        if self.token_count(result) > budget:
            raise ValueError("system prompt and newest turn exceed the context budget")
        self._messages = list(kept)
        return result

    def _turns(self) -> list[list[ChatMessage]]:
        """Group each user message with its following assistant response(s)."""
        turns: list[list[ChatMessage]] = []
        for message in self._messages:
            if message.role == "user":
                turns.append([message])
            elif turns:
                turns[-1].append(message)
        return turns


def rewrite_followup_question(history: Sequence[ChatMessage], question: str) -> str:
    """Rewrite a follow-up question using previous conversation context (LU 3.42)."""
    user_turns = [m.content for m in history if m.role == "user"]
    if not user_turns:
        return question.strip()
    last_query = user_turns[-1].strip()
    q = question.strip()
    if len(q.split()) > 10:
        return q
    anaphora = ("it", "this", "that", "the same", "what about", "how about", "and for", "does it")
    if any(q.lower().startswith(prefix) or f" {prefix} " in f" {q.lower()} " for prefix in anaphora):
        topic_words = [
            w for w in last_query.split()
            if w.lower() not in {"is", "are", "what", "does", "the", "a", "an", "under", "in", "to"}
        ]
        context_hint = " ".join(topic_words[:6])
        if context_hint:
            return f"{q} (regarding {context_hint})"
    return q

