# 08 — Evaluation Contract

Traceability: FR-10, FR-18 · [PRD §5](../docs/PRD.md#5-product-success-metrics--evaluation) · LU 3.36, 3.43

Full methodology and report format: [EVALUATION.md](../docs/EVALUATION.md).

---

## Sets

| Set | Path | Rule |
|---|---|---|
| **Dev** | `evals/dev/dev_set.jsonl` | Free to tune retrieval against |
| **Golden** | `evals/golden/golden_set.jsonl` | **Held out.** Never tuned against, never used to select a config |
| **Scenarios** | `evals/scenarios/` | Multi-turn flows (conversational RAG, LU 3.42) |
| **Baselines** | `evals/baselines/baseline.json` | Recorded run config + results |

> No question used to tune retrieval is reused for final scoring (PRD §5.1).
> This is enforced by a check in the harness: a golden `qid` also present in the
> dev set fails the run.

## Golden Set Composition — minimum 40

| Category | Count | Required behaviour |
|---|---|---|
| `normal_coverage` | 20 | Grounded answer |
| `exclusion_endorsement` | 8 | Answer **+** visible warning |
| `version_conflict` | 6 | Applicable version cited **or** conflict warning |
| `insufficient_evidence` | 6 | **Refuse** to give a definitive answer |

Record schema and field semantics: [EVALUATION.md §2](../docs/EVALUATION.md#2-evaluation-set-composition).

---

## Metrics — normative definitions

| Metric | Definition | Target | Gate |
|---|---|---|---|
| `retrieval_recall_at_5` | `\|{expected_chunk_ids} ∩ {top-5 retrieved}\| / \|{expected_chunk_ids}\|`, per question, averaged | ≥ 0.85 | — |
| `citation_resolution` | Citations resolving to a chunk present in the index ÷ total citations | **1.00** | **Hard** |
| `citation_support` | Statements whose cited evidence entails the statement ÷ statements with citations | ≥ 0.90 | — |
| `grounded_answer_rate` | Answers with no unsupported claim ÷ `grounded` answers | ≥ 0.90 | — |
| `uncertainty_handling` | Insufficient/conflicting questions answered with an uncertainty or review response ÷ those questions | ≥ 0.90 | — |
| `p95_latency_ms` | End-to-end, deployed environment | ≤ 10000 | — |
| `ingestion_success` | Documents yielding text + required metadata ÷ corpus size | ≥ 0.95 | — |
| `warning_coverage` | Relevant questions displaying a warning ÷ those questions | ≥ 0.90 | — |

### Scoring rules that are easy to get wrong

| # | Rule |
|---|---|
| E-1 | `citation_resolution` is **1.00 or fail**. It is never averaged |
| E-2 | Answers with `status != "grounded"` are **excluded** from the grounded-rate denominator and scored under `uncertainty_handling` instead |
| E-3 | A statement with **zero** citations counts against grounded-answer rate, not citation precision |
| E-4 | `must_not_be_cited` chunks appearing in an answer are a **failure**, reported individually |
| E-5 | False confidence — a definitive answer on an `insufficient_evidence` question — is reported per-question; any occurrence is a critical finding |
| E-6 | `n` is reported alongside every percentage — the golden set is small |
| E-7 | Cold starts excluded from p95 are reported separately, never silently dropped |

---

## Harness

```bash
python scripts/evaluate.py --suite golden [--compare-to evals/baselines/baseline.json]
python scripts/evaluate.py --suite golden --stage retrieval   # tuning only, dev set
```

| Stage | Action |
|---|---|
| 1 | Load run config — models, chunk config, k, α, thresholds, corpus checksum |
| 2 | Retrieve for every question |
| 3 | Score retrieval — recall@5, per category, misses with ranks |
| 4 | Generate — guardrails run first; refusals skip generation |
| 5 | Score answers — grounded rate, citation support, citation resolution |
| 6 | Score behaviour — uncertainty handling, warning coverage, forbidden citations |
| 7 | Measure latency — p50/p95/p99 per stage |
| 8 | Report — metrics vs targets, pass/fail, diff vs baseline |

---

## Re-Evaluation Triggers

Re-run the **full** suite when any of these change:

chunk size or overlap · embedding model · vector database · top-K or α ·
retrieval thresholds · reranking on/off · generation model or temperature ·
prompt templates · corpus content or document versions.

> A change that improves one metric while degrading another is **not a pass**.
> Both numbers are reported together, always.

---

## Exit Criteria

- [ ] Golden set of ≥ 40 labelled questions, correctly categorised
- [ ] Dev and golden sets disjoint, verified by the harness
- [ ] All six PRD §5 metrics reported in every run
- [ ] `citation_resolution` enforced as a hard gate
- [ ] Every refusal path scored under `uncertainty_handling`
- [ ] Baseline recorded and committed
- [ ] Re-evaluation triggers documented and followed
- [ ] Known limitations stated in the report (judge estimate, small n, corpus
      representativeness)
