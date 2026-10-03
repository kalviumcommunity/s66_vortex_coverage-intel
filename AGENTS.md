# AGENTS.md

Engineering contract for **Coverage Intel**. Read this before writing code,
adding dependencies, or changing the repository structure.

This file is binding on every automated agent and human contributor working in
this repository.

---

## 1. What this project is

A **retrieval-augmented generation** system that answers insurance coverage
questions for claims adjusters, grounded in approved policy documents and
related authoritative references.

It is **decision support**. It never adjudicates a claim.

## 2. Non-negotiable product rules

These are not style preferences. Breaking one invalidates the product.

1. **No unsupported claims.** Every coverage statement in a generated answer
   must be supported by a retrieved chunk that is cited inline. If support is
   absent, the answer must be an explicit *insufficient evidence* response.
2. **Never fabricate a citation.** A citation must resolve to a real chunk in
   the index — real document ID, section, and page. A missing field is rendered
   as `not available`; it is never invented.
3. **Never silently resolve a conflict.** When two authoritative sources
   disagree and precedence cannot be determined from validated metadata, the
   system surfaces the conflict and requires human review.
4. **Version awareness is mandatory.** An outdated document must never be
   presented as the applicable source. Where effective dates exist, the version
   in effect **on the date of loss** governs.
5. **Endorsements override base policy.** An endorsement always takes precedence
   over the base policy it is linked to.
6. **Never claim to adjudicate.** No code path may approve, deny, settle,
   authorize payment, or modify policy terms. Wording in prompts, UI, and docs
   must position the product as decision support.
7. **No invented facts.** Do not fabricate metrics, baselines, corpus counts,
  stakeholder names, or approval statuses. Unverified items are marked
  `TBD` / `pending validation`.
8. **No sensitive data in logs.** Log query ID, timestamp, chunk IDs, latency,
  and errors. Never log full claim details, policy numbers, or personal data.

## 3. Repository map

| Path | Purpose |
|---|---|
| `docs/` | PRD, UX, technical spec, API, evaluation, deployment, roadmap |
| `specs/` | Numbered build contracts — authoritative for implementation |
| `phases/` | Delivery plan; each phase lists scope and exit criteria |
| `src/coverage_intel/` | Implementation |
| `ui/` | Frontend surfaces |
| `evals/` | Golden set and labelled questions |
| `data/corpus/` | Approved source documents — **git-ignored** |
| `tests/` | Unit and integration tests |
| `scripts/` | CLI entrypoints |

**When changing behaviour, update the matching file in `specs/` in the same
change.** Code and spec must not diverge.

## 4. Implementation conventions

- **Python 3.11+**, typed, `src/` layout, package name `coverage_intel`.
- **Pydantic v2** models for every boundary type (config, chunk metadata,
  retrieval result, API request/response). Metadata is never a bare dict.
- **Immutable-ish domain types** for chunks, evidence, and citations — a
  retrieved chunk is not mutated after indexing.
- **Every chunk carries** `document_id`, `section`, `page`, and a chunk ID.
  `version` and `effective_date` are stored when present; otherwise the chunk
  is flagged `metadata_incomplete=True`.
- **Configuration via environment variables**, never hardcoded secrets, model
  names, thresholds, or paths. All tunables live in `src/coverage_intel/config.py`.
- **Prompts are templates**, versioned in `generation/prompts.py`, not inline
  strings scattered through logic.
- **Structured model output** (JSON schema) for answers — never parse prose
  with regex.
- **Errors are typed.** Retrieval failures, LLM failures, and guardrail
  refusals are distinct outcomes, not a generic exception path.

## 5. RAG pipeline contract

```
ingestion  →  embeddings  →  vectorstore
                                  ↓
query ──────────────────────→  retrieval (semantic + keyword + filters + rerank)
                                  ↓
                            applicability / conflict analysis
                                  ↓
                            context assembly (bounded, ids preserved)
                                  ↓
                            grounded generation (T ≤ 0.2)
                                  ↓
                            citations + guardrails
                                  ↓
                            API / UI + structured logging
```

Stage order is fixed. A stage may be bypassed only by explicit configuration,
and bypassing must be visible in the response payload.

## 6. Working rules

- **One concern per change.** Ingestion changes don't touch generation.
- **Add a spec first, then code.** New behaviour starts in `specs/`.
- **Add a test with the behaviour.** Retrieval and guardrail logic require
  tests; guardrail tests must include a *refusal* case.
- **Run `make check` before pushing** — lint, type-check, and tests.
- **Never commit** `.env`, API keys, real policy documents, or evaluation
  outputs that contain claim details.
- **Small commits, clear messages**, scoped to one phase.

## 7. Evaluation rules

- The **golden set is held out**. Never tune retrieval on an evaluation
  question, and never reuse a tuning question for final scoring.
- Any change to chunking, embedding model, top-K, filters, or reranking must
  be re-evaluated and the result recorded.
- Report retrieval relevance, citation correctness, grounded-answer rate,
  uncertainty handling, and P95 latency. A change that improves one metric
  while silently degrading another is not a pass.

## 8. Phased delivery

Work proceeds in the order defined in [`phases/`](phases/) and traced to Sprint 2
learning units in [`docs/ROADMAP.md`](docs/ROADMAP.md).

Do not begin a later phase while an earlier phase's exit criteria are unmet.
Optional/recommended capabilities (reranking, embedding quality checks,
conversational RAG, caching/monitoring) are additive — they never gate the core
MVP.

## 9. Communication

- Document decisions as ADRs under `docs/adr/` when a choice is non-obvious
  and constrains later work.
- If something in the PRD is unverified or contradicts observed data, raise it
  rather than coding around it silently.
- If a requirement is genuinely ambiguous, ask — do not invent a policy.

## 10. Stack

| Concern | Default | Swappable |
|---|---|---|
| Language | Python 3.11+ | — |
| Package/env | `uv` or `pip` + `venv` | — |
| API | FastAPI + Pydantic v2 | — |
| Vector DB | Chroma (dev) → Qdrant (prod) | yes, behind `VectorStore` interface |
| Embeddings | Provider-configurable | yes, behind `Embedder` interface |
| LLM | Provider-configurable | yes, behind `LLMClient` interface |
| Reranker | Provider cross-encoder | yes, optional |
| Tests | pytest | — |
| Lint/format | ruff | — |
| Types | mypy | — |

Provider-specific code must live behind an interface in `specs/05-retrieval.md`
and `specs/06-generation-and-guardrails.md`, never leak into pipeline logic.
