"""Shared pytest fixtures.

Phase: add fixtures as modules are implemented (phases/phase-02 onward).
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _no_network(monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory) -> None:
    """Guard against accidental live API calls and isolate corpus in unit tests."""
    monkeypatch.setenv("CI_LLM_API_KEY", "test-key")
    monkeypatch.setenv("CI_EMBEDDING_API_KEY", "test-key")
    test_corpus = tmp_path_factory.mktemp("test_corpus")
    monkeypatch.setenv("CI_CORPUS_DIR", str(test_corpus))
    monkeypatch.setenv("PINECONE_INDEX_NAME", "")
    monkeypatch.setenv("PINECONE_API_KEY", "")

    from coverage_intel import config as ci_config
    ci_config._settings = None

    from coverage_intel.vectorstore import index as vs_index
    from coverage_intel.vectorstore.memory import InMemoryVectorStore
    from coverage_intel.vectorstore.schema import CollectionSpec
    vs_index._DEFAULT_STORE = InMemoryVectorStore(CollectionSpec(name="coverage-intel", dimensions=1536))
