# 06 — Generation, Citations & Guardrails Contract

Traceability: FR-11..FR-14, FR-19 · [PRD §9](../docs/PRD.md#9-rag-workflow--application-architecture) stages 8–12 · LU 3.37–3.43

This is the spec that makes the product trustworthy. **A weak answer with a
warning is acceptable. A confident unsupported answer is a defect.**

---

## Stage 8 — Applicability & Conflict Analysis

Runs on retrieved evidence **before** context assembly
([PRD §9.1](../docs/PRD.md#91-applicability-and-source-precedence)).

```python
def analyse(evidence: list[RetrievedEvidence], scenario: Scenario) -> AnalysisResult: ...
```

| # | Check | Rule | Emits |
|---|---|---|---|
| 1 | **Endorsement** | `linked_policy_id` supersedes the base policy chunk | `ENDORSEMENT_APPLIES` |
| 2 | **Version** | `effective_from ≤ date_of_loss ≤ effective_to` | `SUPERSEDED_VERSION` when violated |
| 3 | **Jurisdiction** | Prefer matches when the question names one | `METADATA_INCOMPLETE` on mismatch |
| 4 | **Conflict** | Same topic, differing normative statement, precedence unresolvable | `CONFLICTING_SOURCES` + `REVIEW_REQUIRED` |
| 5 | **Exclusion** | Exclusion/clause language detected in evidence | `EXCLUSION_FOUND` |

### The rule that matters

> **Precedence is resolved only from validated metadata — never from similarity
> score.** A semantically closer document does not outrank the applicable one.

When two authoritative sources disagree and precedence cannot be determined from
metadata, the system **surfaces the conflict and requires human review**. It
never silently selects one.

Provisional precedence rule ([D-02](09-open-questions.md), **awaiting
knowledge-owner confirmation**):

1. An **endorsement** overrides the base policy it is linked to.
2. Among versions of the same document, the one **in effect on the date of loss** applies.

---

## Stage 9 — Context Assembly (FR-11)

```python
def assemble(evidence: list[RetrievedEvidence], budget: int) -> Context: ...
```

| Rule | Detail |
|---|---|
| Budget | `min(CI_MAX_CONTEXT_TOKENS, model_context_limit − output_reserve)` |
| Order | Final score descending (post-rerank if enabled) |
| Packing | Until budget exhausted; truncation **recorded** in `stages` |
| Source identifiers | **Preserved** in every evidence block |
| Excluded evidence | Superseded/conflicting chunks are excluded **or** included with an explicit conflict marker — never dropped silently |

Each block carries a stable citation index so the generated answer can reference
exactly what it was given.

---

## Stage 10 — Grounded Generation (FR-12)

```python
def generate(question: str, scenario: Scenario, context: Context) -> CoverageAnswer: ...
```

| Rule | Detail |
|---|---|
| Temperature | `CI_GENERATION_TEMPERATURE`, **≤ 0.2** — asserted in config |
| Output format | **Structured JSON** against a Pydantic schema — never regex-parsed prose |
| Grounding | Answers may only assert what appears in the context |
| Prompt | Versioned template in `generation/prompts.py`, never an inline string |
| I-7 validation | Every `GROUNDED` statement must carry ≥ 1 valid citation |

### Prompt roles

| Role | Responsibility |
|---|---|
| **System** | Decision-support framing; prohibition on adjudication; citation requirement; refusal instruction |
| **Context** | Numbered evidence blocks with full provenance headers |
| **User** | The question and scenario |

### Hard constraints in the system prompt

- Answer **only** from the provided context.
- Cite every coverage statement.
- If the context does not support an answer, say so explicitly.
- Never state or imply approval, denial, settlement, or coverage guarantee.
- Never invent document IDs, sections, pages, versions, or dates.
- When sources conflict, present both and request review — do not choose.

---

## Stage 11 — Citations (FR-13)

```python
class AnswerStatement(BaseModel):
    text: str
    citation_indices: list[int]      # non-empty when status == GROUNDED
```

| Rule | Detail |
|---|---|
| Verbatim excerpts | `Citation.excerpt` is copied **exactly** from the indexed chunk |
| Resolvability | Every `chunk_id` must exist in the index — a hard gate at eval time |
| Missing fields | Rendered `not available`; never omitted, never invented |
| Inline markers | `[1] [2]` link to the evidence list |

A generated citation that does not resolve **fails the answer**, it does not
degrade gracefully into an approximate reference.

---

## FR-14 — Guardrails

Evaluated **before** generation. First trigger wins.

```python
def evaluate(evidence: list[RetrievedEvidence], analysis: AnalysisResult) -> GuardrailResult: ...
```

| # | Condition | Result |
|---|---|---|
| 1 | No evidence retrieved | `INSUFFICIENT_EVIDENCE` |
| 2 | `top_semantic_score < CI_SIMILARITY_THRESHOLD` | `WEAK_EVIDENCE` + `LOW_SIMILARITY` |
| 3 | No chunk ≥ `CI_RELEVANCE_FLOOR` | `INSUFFICIENT_EVIDENCE` |
| 4 | Unresolved conflict | `CONFLICTING` + `REVIEW_REQUIRED` |
| 5 | All supporting chunks `metadata_incomplete` | `WEAK_EVIDENCE` + `METADATA_INCOMPLETE` |

### Invariants

| # | Invariant |
|---|---|
| G-1 | When a guardrail triggers, generation is **skipped or strictly constrained** |
| G-2 | The system **never** degrades to an unevidenced answer |
| G-3 | A refusal returns HTTP **200** — it is a correct product outcome, not a failure |
| G-4 | A refusal still returns the evidence considered, so the adjuster can judge |
| G-5 | `CI_SIMILARITY_THRESHOLD` is **calibrated on the golden set**, never guessed or inherited |

### Threshold calibration

Score distributions differ per embedding model. The threshold is derived by
running the set with the guardrail disabled, separating scores for questions
**with** and **without** supporting evidence, and choosing a split — then
reporting the false-refusal rate on `normal_coverage` questions (budget ≤ 10%).

A threshold that maximises the score by refusing everything is **not** valid.

---

## FR-19 — Logging

```python
{
  "query_id": "q_01J...",
  "timestamp": "2026-01-01T00:00:00Z",
  "filters": {...},
  "retrieved_chunk_ids": ["c_a1b2", "c_c3d4"],
  "answer_status": "grounded",
  "warnings": ["exclusion_found"],
  "latency_ms": {"retrieval": 310, "rerank": 0, "generation": 2410, "total": 2830},
  "error": null
}
```

| Logged | Never logged |
|---|---|
| Query ID, timestamp | Question text containing claim details |
| Chunk **IDs** | Chunk text |
| Scores, filters | Policy numbers, names, personal data |
| Latency per stage | Full request/response bodies |
| Warning kinds | Uploaded document contents |

> Claim context makes the API **stateful** in substance. The MVP does not persist
> transcripts by default; if that changes, it needs the security reviewer's
> sign-off ([PRD §11](../docs/ROADMAP.md#blockers--external-dependencies)).

---

## Exit Criteria

- [ ] Applicability analysis handles endorsement / version / jurisdiction / conflict / exclusion
- [ ] Precedence derives from metadata only — a test asserts similarity never decides precedence
- [ ] Context assembly respects the budget and records truncation
- [ ] Generation temperature asserted ≤ 0.2
- [ ] Output is structured JSON validated against the schema
- [ ] Every `GROUNDED` statement carries a resolvable citation
- [ ] **All five guardrail triggers have tests, including the refusal path**
- [ ] Refusals return HTTP 200 with evidence attached
- [ ] Threshold calibration procedure implemented and documented
- [ ] Log audit confirms no claim content or personal data
