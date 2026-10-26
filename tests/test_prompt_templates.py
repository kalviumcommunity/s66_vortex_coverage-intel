"""Tests for reusable prompt templates."""

from __future__ import annotations

import pytest

from coverage_intel.generation.prompts import TEMPLATES, PromptTemplate


def test_template_renders_named_placeholders() -> None:
    template = PromptTemplate("greeting", "Hello {name}; question: {question}")

    assert template.placeholders == {"name", "question"}
    assert template.render(name="adjuster", question="What is covered?") == (
        "Hello adjuster; question: What is covered?"
    )


@pytest.mark.parametrize(
    "values",
    [{"name": "adjuster"}, {"name": "adjuster", "question": "Q", "extra": "bad"}],
)
def test_template_rejects_missing_or_unexpected_values(values: dict[str, str]) -> None:
    with pytest.raises(ValueError):
        PromptTemplate("greeting", "Hello {name}; question: {question}").render(**values)


def test_versioned_templates_are_named_and_reusable() -> None:
    assert TEMPLATES["grounded_answer"].name == "grounded_answer"
    assert "{question}" in TEMPLATES["grounded_answer"].template
