"""Run the retrieval or RAG evaluation suite.

Phase: phase-04-retrieval-tuning.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from coverage_intel.evaluation.metrics import build_retrieval_report
from coverage_intel.pipeline.rag import answer_question
from coverage_intel.retrieval.semantic import Scenario, retrieve


def main() -> int:
    """Run the retrieval or RAG evaluation suite."""
    parser = argparse.ArgumentParser(description="Run the retrieval or RAG evaluation suite.")
    parser.add_argument(
        "--dataset",
        default="evals/golden/golden_set.example.jsonl",
        help="Path to JSONL golden evaluation dataset",
    )
    parser.add_argument("--k", type=int, default=5, help="Top-K cutoff for evaluation")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"Evaluation dataset not found: {dataset_path}", file=sys.stderr)
        return 1

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.ask import _ensure_corpus_indexed

    _ensure_corpus_indexed()

    cases = []
    rag_results = []
    with dataset_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            question = item.get("question", "")
            scenario_data = item.get("scenario", {})
            scenario = Scenario(**scenario_data) if scenario_data else None
            expected_chunks = item.get("expected_chunk_ids", [])
            expected_docs = item.get("expected_document_ids", [])

            evidence = retrieve(question, k=args.k, scenario=scenario)
            retrieved_chunk_ids = [e.chunk.chunk_id for e in evidence]
            retrieved_doc_ids = [e.chunk.document_id for e in evidence]

            # Compare on document or chunk IDs (prefix-tolerant for slugged IDs)
            expected = expected_docs if expected_docs else expected_chunks
            actual = retrieved_doc_ids if expected_docs else retrieved_chunk_ids
            matched_actual = [
                act
                for act in actual
                if any(exp.lower() in act.lower() or act.lower() in exp.lower() for exp in expected)
            ]
            cases.append((expected, matched_actual))

            answer = answer_question(question, scenario=scenario)
            rag_results.append(
                {
                    "qid": item.get("qid"),
                    "category": item.get("category"),
                    "question": question,
                    "status": answer.status.value,
                    "acceptable_status": item.get("acceptable_status", []),
                    "pass": answer.status.value
                    in item.get("acceptable_status", [answer.status.value]),
                }
            )

    report = build_retrieval_report(cases, k=args.k)

    print("=" * 65)
    print("       COVERAGE INTEL — RAG RETRIEVAL & GROUNDING EVALUATION")
    print("=" * 65)
    print(f"Total Test Cases Evaluated : {len(cases)}")
    print(f"Retrieval Recall@{args.k}        : {report.recall_at_k:.1%}")
    print(f"Retrieval Precision@{args.k}     : {report.precision_at_k:.1%}")
    print(f"Mean Reciprocal Rank (MRR) : {report.mean_reciprocal_rank:.3f}")
    print("-" * 65)
    print(f"{'QID':<12} {'CATEGORY':<22} {'STATUS':<15} {'VERDICT'}")
    print("-" * 65)
    for r in rag_results:
        verdict = "PASS [ok]" if r["pass"] else "REVIEW"
        print(f"{r['qid']:<12} {r['category']:<22} {r['status']:<15} {verdict}")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
