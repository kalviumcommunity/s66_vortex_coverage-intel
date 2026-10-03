# Evaluation Sets

Implementation of FR-10 and FR-18. Methodology:
[docs/EVALUATION.md](../docs/EVALUATION.md) · Contract:
[specs/08-evaluation.md](../specs/08-evaluation.md).

## Structure

```
evals/
├── dev/         tuning set — free to iterate against
├── golden/      HELD OUT — never tuned against, never used to select a config
├── scenarios/   multi-turn flows (conversational RAG, LU 3.42)
├── baselines/   recorded run configs + results
└── reports/     generated — git-ignored (may contain claim-derived content)
```

## The held-out rule

**No question used to tune retrieval is reused for final scoring** (PRD §5.1).

The harness fails the run if a golden `qid` also appears in the dev set. Tuning
on `dev/`; score on `golden/`.

## Golden Set Composition — minimum 40

| Category | Count |
|---|---|
| `normal_coverage` | 20 |
| `exclusion_endorsement` | 8 |
| `version_conflict` | 6 |
| `insufficient_evidence` | 6 |

## Record Schema

See [`golden/schema.json`](golden/schema.json) and the worked example in
[`golden/golden_set.example.jsonl`](golden/golden_set.example.jsonl).

## Running

```bash
make eval                              # full golden suite
make eval-retrieval                    # retrieval only, dev set — for tuning
python scripts/evaluate.py --suite golden --compare-to evals/baselines/baseline.json
```
