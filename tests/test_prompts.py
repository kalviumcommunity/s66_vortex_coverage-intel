"""Tests for system/user prompt role construction."""

from __future__ import annotations

import pytest

from coverage_intel.generation.prompts import SYSTEM_ROLE, build_grounded_messages, build_messages


def test_build_messages_preserves_system_then_user_roles() -> None:
    messages = build_messages("Follow the policy evidence.", "Is hail covered?")

    assert [message.role for message in messages] == ["system", "user"]
    assert messages[0].content == "Follow the policy evidence."
    assert messages[1].content == "Is hail covered?"


def test_grounded_prompt_keeps_instructions_in_system_message() -> None:
    system, user = build_grounded_messages("Is hail covered?", "[1] Exclusion: hail damage")

    assert system.content == SYSTEM_ROLE
    assert "Is hail covered?" in user.content
    assert "[1] Exclusion: hail damage" in user.content


@pytest.mark.parametrize("system_prompt,user_prompt", [("", "question"), ("rules", "")])
def test_empty_roles_are_rejected(system_prompt: str, user_prompt: str) -> None:
    with pytest.raises(ValueError):
        build_messages(system_prompt, user_prompt)
