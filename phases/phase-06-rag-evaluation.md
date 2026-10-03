# Phase 06 — RAG Evaluation

**LUs:** 3.43 (Core) · **Status:** ⬜
**Spec:** [08](../specs/08-evaluation.md) · [EVALUATION.md](../docs/EVALUATION.md)

---

## Scope

Measure the **answers**, not just the retrieval. Retrieval can be excellent while
the generator still overstates what the evidence says.

## Tasks

- [ ] Build `evals/golden/golden_set.jsonl` — ≥ 40 labelled questions:
  - [ ] 20 `normal_coverage`
  - [ ] 8 `exclusion_endorsement`
  - [ ] 6 `version_conflict`
  - [ ] 6 `insufficient_evidence`
- [ ] Verify dev ∩ golden = ∅ in the harness
- [ ] `evaluation/runner.py` — full pipeline over the golden set
- [ ] Citation **support** scoring (LLM judge, forced binary + rationale)
- [ ] Citation **resolution** scoring (index lookup) — hard gate
- [ ] Grounded-answer rate — statement-level unsupported-claim detection
- [ ] Uncertainty handling + false-confidence detection
- [ ] Warning coverage
- [ ] Latency instrumentation (p50/p95/p99, per stage)
- [ ] Record `evals/baselines/baseline.json`
- [ ] Manual spot-check of judged samples each run

## Exit Criteria

- [ ] All six PRD §5 metrics reported
- [ ] `retrieval_recall_at_5` ≥ 0.85
- [ ] `citation_support` ≥ 0.90 **and** `citation_resolution` == **1.00**
- [ ] `grounded_answer_rate` ≥ 0.90
- [ ] `uncertainty_handling` ≥ 0.90, with **zero** false-confidence answers on
      `insufficient_evidence` questions
- [ ] `p95_latency_ms` ≤ 10 000
- [ ] `must_not_be_cited` violations: **zero**
- [ ] Baseline committed; `n` reported alongside every percentage
- [ ] Known limitations stated in the report

## Reporting rule

A metric that passes while another regresses is **not a pass**. Both numbers are
reported together.
