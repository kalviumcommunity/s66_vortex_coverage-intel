# Phase 04 — Retrieval Tuning & Evaluation

**LUs:** 3.36 (Core) · **Status:** ⬜ Blocked on Q-06, D-02
**Spec:** [05](../specs/05-retrieval.md) · [08](../specs/08-evaluation.md)

---

## Scope

Make retrieval meet its target **before** any generation exists. Tuning a
generator on bad retrieval produces answers that look grounded and are not.

## Tasks

- [ ] Build `evals/dev/` tuning set — separate from golden
- [ ] `evaluation/metrics.py` — `recall@k`, per-category, misses with ranks
- [ ] `scripts/evaluate.py --stage retrieval`
- [ ] Tuning sweep in documented order:
  1. Chunk size / overlap
  2. α (dense vs. sparse)
  3. Candidate pool size
  4. Metadata filters
  5. Reranking *(Recommended — evaluate, do not assume)*
- [ ] Record every config tried and its score
- [ ] Identify whether failures are retrieval, metadata, or corpus problems

## Exit Criteria

- [ ] `recall@5` ≥ **0.85** on the dev suite
- [ ] Per-category recall reported; category-specific weaknesses understood
- [ ] Every tuning decision recorded with its measurement
- [ ] Retrieval works with reranking **disabled**
- [ ] Misses analysed — not merely counted

## Rule

Tune on `evals/dev/` only. The golden set is held out and is not consulted
during tuning.

## Blockers

| Blocker | Owner |
|---|---|
| Q-06 — evaluation set approval | Project team / reviewer |
| D-02 — precedence rule | Knowledge / UW / compliance |
