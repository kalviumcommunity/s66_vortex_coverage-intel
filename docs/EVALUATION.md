# Evaluation Specification — Coverage Intel

> Implements FR-10, FR-18. Defines how every PRD §5 metric is measured.
> A metric without a measurement method is not a metric.

---

## 1. Principles

1. **The golden set is held out.** No question used to tune retrieval is reused
   for final scoring (PRD §5.1).
2. **Dev and eval sets are separate files.** `evals/dev/` may be tuned against
   freely. `evals/golden/` may not.
3. **Every run is reproducible.** The run records model names, chunk config,
   top-K, α, thresholds, and corpus checksum.
4. **A regression in any metric fails the run**, even if another metric improved.

---

## 2. Evaluation Set Composition

`evals/golden/golden_set.jsonl` — minimum 40 labelled questions.

| Category | Count | Expected behaviour |
|---|---|---|
| `normal_coverage` | 20 | Answer grounded in retrieved policy language |
| `exclusion_endorsement` | 8 | Answer **plus** a visible exclusion/endorsement warning |
| `version_conflict` | 6 | Cite the version in effect on the date of loss, **or** raise a conflict warning |
| `insufficient_evidence` | 6 | **Refuse** to give a definitive answer |

### Record schema

```json
{
  "qid": "vconf-001",
  "category": "version_conflict",
  "question": "Which version of the HO-3 wording applied on 14 March 2025?",
  "scenario": {
    "policy_type": "HO-3",
    "date_of_loss": "2025-03-14",
    "jurisdiction": "CA"
  },
  "expected_document_ids": ["POL-HO3-2023", "POL-HO3-2024"],
  "expected_chunk_ids": ["c_ho3_2023_s1", "c_ho3_2024_s1"],
  "expected_applicable_document_id": "POL-HO3-2024",
  "expected_warnings": ["version_conflict"],
  "must_not_be_cited": ["c_ho3_2023_retired_s1"],
  "acceptable_status": ["grounded", "conflicting"]
}
```

| Field | Purpose |
|---|---|
| `expected_chunk_ids` | Retrieval-relevance ground truth |
| `expected_applicable_document_id` | Version-conflict ground truth |
| `must_not_be_cited` | Catches a superseded version being presented as current |
| `expected_warnings` | Drives the warning-coverage metric |
| `acceptable_status` | A refusal is a **pass** for `insufficient_evidence` questions |

---

## 3. Metrics

### 3.1 Retrieval Relevance — target ≥ 85%

```
retrieval_recall@k = |{expected_chunk_ids} ∩ {top-k retrieved chunk_ids}| / |{expected_chunk_ids}|
```

Measured with `k = 5`. A question is a *hit* when `recall@5 ≥ 1.0` for at least
one expected chunk; per-question recall is also reported.

**Reported:** overall recall@5, per-category recall, and the list of misses with
their retrieved ranks (misses are the retrieval-tuning work queue).

### 3.2 Citation Correctness — target ≥ 90% support, 100% resolve

Two independent measurements:

**Resolution (hard gate).**
```
resolution_rate = citations resolving to a chunk_id present in the index
                / total citations
```
A citation pointing at a non-existent chunk is a **hard failure** — never a
percentage to average away.

**Support (entailment).**
```
citation_precision = statements whose cited evidence entails the statement
                   / total statements carrying citations
```
Judged by an LLM judge with a forced binary output plus a rationale, and
spot-checked by hand. A statement with **zero** citations counts against the
grounded-answer rate, not against citation precision.

### 3.3 Grounded Answer Rate — target ≥ 90%

```
grounded_rate = answers with no unsupported claim / total grounded answers
```

Each answer is decomposed into statements; every statement is checked against
the retrieved evidence. **Unsupported claims** are the failure signal.

An answer with `status != "grounded"` is excluded from this denominator and
evaluated under §3.4 instead — a refusal is not a grounding failure.

### 3.4 Uncertainty / Escalation Handling — target ≥ 90%

```
uncertainty_rate = questions where the system returned an uncertainty/review
                   response instead of a definitive answer
                 / questions labelled insufficient-evidence or conflicting
```

Also measures **false confidence**: definitive answers on
`insufficient_evidence` questions. Any such case is reported individually —
these are the most damaging failures in the product.

| | Correct behaviour | Failure |
|---|---|---|
| `insufficient_evidence` | `status = insufficient_evidence` + warning | A confident coverage answer |
| `version_conflict` | Applicable version cited, or conflict warning | Silently citing a superseded version |

### 3.5 Response Latency — target ≤ 10 s P95

Measured **end-to-end in the deployed environment**: request submitted → full
response received. Reported as p50 / p95 / p99, plus a per-stage breakdown
(`retrieval_ms`, `rerank_ms`, `generation_ms`).

Cold start and provider warm-up are excluded, but recorded separately — an
excluded cold start must be visible in the report.

### 3.6 Document Ingestion Success — target ≥ 95%

```
ingestion_success = documents producing non-empty extracted text
                    + all required metadata fields
                  / total documents in the test corpus
```

Reported alongside: extraction character counts, chunk counts, and a list of
documents flagged `metadata_incomplete` with their missing fields.

---

## 4. Harness Design

```
scripts/evaluate.py --suite golden [--compare-to baseline.json] [--report out.json]
```

| Stage | What it does |
|---|---|
| 1. Load run config | model names, chunk config, k, α, thresholds, corpus checksum |
| 2. Retrieve | Run hybrid retrieval for every question |
| 3. Score retrieval | recall@5, per-category, misses with ranks |
| 4. Generate | Guardrails run first — refusals skip generation |
| 5. Score answers | Grounded rate, citation support, citation resolution |
| 6. Score behaviour | Uncertainty handling, warning coverage, forbidden-citation checks |
| 7. Measure latency | p50/p95/p99 per stage |
| 8. Report | Metrics vs PRD §5 targets, pass/fail per metric, diff vs baseline |

### Output

```json
{
  "run_id": "eval_20260101_120000",
  "config": { "embedding_model": "…", "llm_model": "…", "top_k": 5, "alpha": 0.7,
              "similarity_threshold": 0.35, "chunk_size": 500, "chunk_overlap": 50,
              "rerank_enabled": false, "corpus_checksum": "sha256:…" },
  "metrics": {
    "retrieval_recall_at_5":  { "value": 0.87, "target": 0.85, "pass": true },
    "citation_resolution":   { "value": 1.00, "target": 1.00, "pass": true },
    "citation_support":      { "value": 0.91, "target": 0.90, "pass": true },
    "grounded_answer_rate":  { "value": 0.92, "target": 0.90, "pass": true },
    "uncertainty_handling":  { "value": 0.94, "target": 0.90, "pass": true },
    "p95_latency_ms":        { "value": 6430, "target": 10000, "pass": true },
    "ingestion_success":     { "value": 0.96, "target": 0.95, "pass": true }
  },
  "failures": [ … ],
  "retrieval_misses": [ … ]
}
```

---

## 5. Thresholds Are Calibrated, Not Guessed

`CI_SIMILARITY_THRESHOLD` (FR-14) cannot be a guessed constant — score
distributions differ per embedding model and per corpus.

**Calibration procedure:**
1. Run the golden set with the guardrail threshold effectively disabled
   (`0.0`), recording every question's top similarity score.
2. Separate scores for questions **with** known supporting evidence from those
   **without**.
3. Choose a threshold that correctly refuses the insufficient-evidence questions
   while retaining the normal ones.
4. Record the chosen value and its justification in the run config.

A threshold that maximises the eval score by refusing everything is not
acceptable — refusal rate on `normal_coverage` questions is reported alongside
and must stay below the false-refusal budget (target ≤ 10%).

---

## 6. Re-Evaluation Triggers

Re-run the full suite when **any** of these change:

- chunk size or overlap
- embedding model
- vector database
- top-K or hybrid α
- retrieval thresholds
- reranking enabled/disabled
- generation model or temperature
- prompt templates
- corpus content or document versions

A change that improves one metric while degrading another is **not a pass**.

---

## 7. Files

```
evals/
├── dev/                 # tuning set — free to iterate against
│   └── dev_set.jsonl
├── golden/              # HELD OUT — never tuned against
│   └── golden_set.jsonl
├── scenarios/           # multi-turn / conversational scenarios (LU 3.42)
├── baselines/           # recorded run configs + results
│   └── baseline.json
└── reports/             # generated — git-ignored
```

---

## 8. Known Limitations

Stated plainly rather than glossed over:

- LLM-as-judge citation support is an estimate, not ground truth. Spot-check
  samples manually each run.
- The golden set is small (40) by PRD definition, so metric confidence intervals
  are wide. Report n alongside every percentage.
- Synthetic or representative corpora are not the production corpus; retrieval
  metrics may shift against real documents.
- PDF extraction quality depends on the source files. Scanned documents require
  OCR, which is **not** in MVP scope (PRD §10).
