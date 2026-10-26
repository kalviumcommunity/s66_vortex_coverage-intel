"""Ask a coverage question from the command line.

Phase: phase-05-rag-core.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from coverage_intel.config import get_settings
from coverage_intel.embeddings.encoder import get_embedder
from coverage_intel.ingestion.chunking import chunk
from coverage_intel.ingestion.validation import prepare_corpus
from coverage_intel.pipeline.rag import answer_question
from coverage_intel.retrieval.semantic import Scenario
from coverage_intel.vectorstore.index import get_vector_store


def _ensure_corpus_indexed() -> None:
    """Ensure corpus is indexed in the vector store before answering."""
    store = get_vector_store()
    if store.count > 0:
        return
    settings = get_settings()
    corpus_path = Path(settings.corpus_dir)
    if not corpus_path.exists():
        return
    files = [p for p in corpus_path.iterdir() if p.is_file() and not p.name.startswith(".")]
    if not files:
        return
    docs, _ = prepare_corpus(files)
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk(doc.blocks))
    if not all_chunks:
        return
    embedder = get_embedder(settings)
    texts = [c.text for c in all_chunks]
    vectors = embedder.embed_documents(texts)
    store.upsert(all_chunks, vectors)


def main() -> int:
    """Ask a coverage question from the command line."""
    parser = argparse.ArgumentParser(description="Ask a coverage question from the command line.")
    parser.add_argument("question", nargs="?", default=os.getenv("QUESTION", ""), help="Coverage question")
    parser.add_argument("--json", action="store_true", help="Output raw JSON response")
    parser.add_argument("--jurisdiction", default=None, help="Jurisdiction code (e.g. CA, FL)")
    parser.add_argument("--policy-type", default=None, help="Policy type (e.g. HO-3)")
    parser.add_argument("--date-of-loss", default=None, help="Date of loss (YYYY-MM-DD)")
    args = parser.parse_args()

    question = args.question.strip()
    if not question:
        print("Error: No question provided. Pass a question as an argument or set QUESTION env var.", file=sys.stderr)
        return 1

    _ensure_corpus_indexed()

    scenario = None
    if args.jurisdiction or args.policy_type or args.date_of_loss:
        scenario = Scenario(
            jurisdiction=args.jurisdiction,
            policy_type=args.policy_type,
        )

    answer = answer_question(question, scenario=scenario)

    if args.json:
        print(answer.model_dump_json(indent=2))
        return 0

    print("=" * 60)
    print(f"QUESTION : {answer.question}")
    print(f"STATUS   : {answer.status.value.upper()}")
    print("=" * 60)
    print(f"\nSUMMARY:\n{answer.summary}\n")

    if answer.warnings:
        print("WARNINGS:")
        for w in answer.warnings:
            print(f"  [{w.severity.upper()}] {w.kind.value}: {w.message}")
        print()

    if answer.citations:
        print(f"CITATIONS ({len(answer.citations)}):")
        for c in answer.citations:
            sec = f" | Section: {c.section}" if c.section else ""
            pg = f" | Page: {c.page}" if c.page else ""
            print(f"  [{c.citation_index}] {c.document_id}{sec}{pg}")
            print(f"      \"{c.excerpt[:120]}...\"")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
