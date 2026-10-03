"""BM25 keyword retrieval.

Policy language is lexically specific — defined terms, clause numbers — so
keyword retrieval carries signal that pure semantic search drops.

Spec: specs/05-retrieval.md
"""

from __future__ import annotations


class KeywordIndex:
    """BM25 index over chunk text."""

    def search(self, query: str, k: int, filters: "object | None" = None):
        """Return the top-k chunks by BM25 score."""
        raise NotImplementedError("Implemented in phase-03-embeddings-and-vector-db.md")
