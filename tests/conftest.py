"""Shared pytest fixtures.

Phase: add fixtures as modules are implemented (phases/phase-02 onward).
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Guard against accidental live API calls in the unit test suite."""
    monkeypatch.setenv("CI_LLM_API_KEY", "test-key")
    monkeypatch.setenv("CI_EMBEDDING_API_KEY", "test-key")
