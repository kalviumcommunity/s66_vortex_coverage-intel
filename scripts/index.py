"""Embed chunked documents and build the vector index.

Phase: phase-03-embeddings-and-vector-db.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from coverage_intel.config import get_settings
from coverage_intel.embeddings.encoder import get_embedder
from coverage_intel.ingestion.chunking import chunk
from coverage_intel.ingestion.validation import prepare_corpus
from coverage_intel.vectorstore.index import get_vector_store


def main() -> int:
    """Embed chunked documents and build the vector index."""
    parser = argparse.ArgumentParser(
        description="Embed chunked documents and build the vector index."
    )
    parser.add_argument("--corpus-dir", default=None, help="Directory containing source documents")
    args = parser.parse_args()

    settings = get_settings()
    corpus_path = Path(args.corpus_dir or settings.corpus_dir)
    if not corpus_path.exists():
        print(f"Corpus directory not found: {corpus_path}", file=sys.stderr)
        return 1

    files = [p for p in corpus_path.iterdir() if p.is_file() and not p.name.startswith(".")]
    if not files:
        print(f"No documents found in {corpus_path}", file=sys.stderr)
        return 0

    print(f"Ingesting documents from {corpus_path}...")
    documents, _ = prepare_corpus(files)
    if not documents:
        print("No valid documents to index.", file=sys.stderr)
        return 1

    all_chunks = []
    for doc in documents:
        doc_chunks = chunk(doc.blocks)
        all_chunks.extend(doc_chunks)

    print(f"Embedding {len(all_chunks)} chunks...")
    embedder = get_embedder(settings)
    texts = [c.text for c in all_chunks]
    vectors = embedder.embed_documents(texts)

    print("Indexing into vector store...")
    store = get_vector_store()
    store.upsert(all_chunks, vectors)

    print(f"Successfully indexed {store.count} chunks into the vector store.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
