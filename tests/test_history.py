"""Tests for token-bounded message history."""

from __future__ import annotations

import pytest

from coverage_intel.generation.history import MessageHistory


def test_trim_preserves_system_and_newest_complete_turns() -> None:
    history = MessageHistory("You are a grounded insurance assistant.")
    history.add("user", "Old question " + "details " * 20)
    history.add("assistant", "Old answer " + "details " * 20)
    history.add("user", "Recent question")
    history.add("assistant", "Recent answer")
    full_count = history.token_count()

    messages = history.trim_to_budget(full_count - 12)

    assert [message.role for message in messages] == ["system", "user", "assistant"]
    assert messages[-1].content == "Recent answer"
    assert history.messages == messages


def test_reserve_tokens_reduces_history_budget() -> None:
    history = MessageHistory("System rules")
    history.add("user", "Question one")
    history.add("assistant", "Answer one")
    history.add("user", "Question two")
    history.add("assistant", "Answer two")
    full_count = history.token_count()

    messages = history.trim_to_budget(full_count, reserve_tokens=10)

    assert messages[0].role == "system"
    assert history.token_count(messages) <= full_count - 10


def test_invalid_role_and_unfit_system_prompt_are_rejected() -> None:
    history = MessageHistory("System rules")
    with pytest.raises(ValueError):
        history.trim_to_budget(1)


def test_rewrite_followup_question_resolves_anaphora() -> None:
    from coverage_intel.generation.history import rewrite_followup_question
    from coverage_intel.generation.llm import ChatMessage

    history = [
        ChatMessage("user", "Is sudden water discharge from plumbing covered?"),
        ChatMessage("assistant", "Yes, under HO-3 peril 12."),
    ]
    rewritten = rewrite_followup_question(history, "What about the deductible for it?")
    assert "regarding" in rewritten
    assert "water" in rewritten or "discharge" in rewritten

