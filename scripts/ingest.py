"""Parse, clean, and chunk approved documents from the corpus directory.

Phase: phase-02-ingestion.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from coverage_intel.config import get_settings
from coverage_intel.ingestion.chunking import chunk
from coverage_intel.ingestion.validation import prepare_corpus


def main() -> int:
    """Parse, clean, and chunk approved documents from the corpus directory."""
    parser = argparse.ArgumentParser(
        description="Parse, clean, and chunk approved documents from the corpus directory."
    )
    parser.add_argument("--corpus-dir", default=None, help="Directory containing source documents")
    parser.add_argument("--validate", action="store_true", help="Run validation report")
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

    print(f"Loading and validating {len(files)} document(s) from {corpus_path}...")
    documents, report = prepare_corpus(files)
    print(f"Corpus: {report.total} document(s)")
    print(f"  Indexed successfully : {report.indexed} ({report.success_rate:.1%})")
    print(f"  Failed validation    : {report.failed}")
    for fail in report.failures:
        print(f"    - {fail.path}: [{fail.code}] {fail.message}")

    total_chunks = 0
    for doc in documents:
        doc_chunks = chunk(doc.blocks)
        total_chunks += len(doc_chunks)
    print(f"Generated {total_chunks} chunk(s) across {len(documents)} document(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
