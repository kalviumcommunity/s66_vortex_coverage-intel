# Roadmap & Sprint 2 Learning Unit Traceability

> Phase-by-phase plans live in [`phases/`](../phases/). This document is the
> index and the LU mapping.

---

## Principle

**Core capabilities gate the MVP. Recommended and optional capabilities do not.**

- **Core** — must ship. The MVP is incomplete without it.
- **Recommended** — strongly useful, additive. Never blocks core delivery.
- **Optional** — may be skipped entirely.

Skipping every Recommended and Optional unit still yields a complete MVP, as
long as the underlying required *behaviour* is implemented.

---

## Phase Overview

| Phase | Name | LUs | Tier | Depends on |
|---|---|---|---|---|
| [00](../phases/phase-00-foundation.md) | Foundation & Repository | 3.11 | Core | — |
| [01](../phases/phase-01-llm-and-prompting.md) | LLM Access & Prompting | 3.12–3.18 | Core | 00 |
| [02](../phases/phase-02-ingestion.md) | Ingestion & Chunking | 3.19–3.24 | Core | 00 |
| [03](../phases/phase-03-embeddings-and-vector-db.md) | Embeddings & Vector DB | 3.25–3.34 | Core | 02 |
| [04](../phases/phase-04-retrieval-tuning.md) | Retrieval Tuning & Eval | 3.36 | Core | 03 |
| [05](../phases/phase-05-rag-core.md) | RAG Core & Guardrails | 3.37–3.41 | Core | 04 |
| [06](../phases/phase-06-rag-evaluation.md) | RAG Evaluation | 3.43 | Core | 05 |
| [07](../phases/phase-07-backend-api.md) | Backend API | 3.44–3.45 | Core | 05 |
| [08](../phases/phase-08-frontend-ui.md) | Frontend UI | 3.46–3.47 | Core | 07 |
| [09](../phases/phase-09-deployment-and-docs.md) | Deployment & Submission | 3.49–3.50 | Core | 08 |
| [10](../phases/phase-10-recommended-and-optional.md) | Recommended & Optional | 3.29, 3.35, 3.42, 3.47s, 3.48 | Rec./Opt | any Core phase |

---

## Full LU Traceability

| LU | Capability | Tier | Phase | PRD FR |
|---|---|---|---|---|
| 3.11 | GitHub Repository & Team Workflow | Core | 00 | — |
| 3.12–3.13 | LLM API Access; Prompt Construction & Roles | Core | 01 | FR-12 |
| 3.17–3.18 | Structured Output / JSON; Prompt Templates | Core | 01 | FR-12 |
| 3.19–3.24 | Document Loading, Extraction, Cleaning, Chunking, Metadata, Corpus Validation | Core | 02 | FR-01–FR-05 |
| 3.25–3.27 | Embeddings Fundamentals/API; Similarity & Distance | Core | 03 | FR-06 |
| 3.29 | Embedding Quality Checks | **Recommended** | 10 | FR-06 |
| 3.30–3.34 | Vector DB, Indexing, Top-K Search, Metadata/Hybrid Search, Retrieval Tuning | Core | 03, 04 | FR-07–FR-09 |
| 3.35 | Re-ranking | **Recommended** | 10 | FR-08 |
| 3.36 | Retrieval Evaluation | Core | 04 | FR-10 |
| 3.37–3.41 | RAG Architecture, Context Injection, Grounded Generation, Citations, Guardrails | Core | 05 | FR-11–FR-14 |
| 3.42 | Conversational RAG | **Recommended / Conditional** | 10 | — |
| 3.43 | RAG Evaluation | Core | 06 | FR-18 |
| 3.44–3.45 | Backend API; Upload/Indexing Endpoint | Core | 07 | FR-15, FR-16 |
| 3.46 | Chat UI | Core | 08 | FR-17 |
| 3.47 | Citation Display | Core | 08 | FR-13 |
| 3.47 (streaming) | Streaming Generation | **Optional** | 10 | — |
| 3.48 | Caching / Logging / Monitoring | **Recommended** | 10 | FR-19 |
| 3.49–3.50 | Deployment / Documentation; Final Submission | Core | 09 | FR-20 |

### Optional LUs — explicitly skippable

| LU | Why skippable | Required behaviour that remains |
|---|---|---|
| 3.14 Tokens | Implementation detail | Chunks still respect the configured token budget |
| 3.15 Context Windows | Implementation detail | Context still bounded to the model limit |
| 3.16 Model Parameters | Implementation detail | Temperature still ≤ 0.2 |
| 3.28 Batch Embedding / Rate / Cost | Optimisation | Embeddings still generated for every validated chunk |
| 3.47 streaming | UX polish only | Citation display is **not** optional and remains core |

---

## Critical Path

```
00 ──▶ 01 ──────────────┐
 │                       │
 └─▶ 02 ──▶ 03 ──▶ 04 ──┼──▶ 05 ──┬──▶ 06 ──┐
                            │       │         │
                            └───────┴──▶ 07 ──┴──▶ 08 ──▶ 09
```

Phase 01 (LLM access) and Phase 02 (ingestion) can run in parallel. Phase 10 is
independent and can be pulled in at any point.

---

## Blockers — External Dependencies

These are **not** code problems. They gate delivery and are tracked against the
project/business owner.

| Blocker | Blocks | Owner | Status |
|---|---|---|---|
| Approved document corpus | Phase 02 onward | Knowledge owner | ⏳ Pending |
| Source authority & precedence confirmation (D-02) | Phase 04, Phase 05 | Knowledge / UW / compliance | ⏳ Pending |
| Metadata availability (version, effective date, jurisdiction) | Phase 02, 03 | Knowledge owner | ⏳ Pending |
| LLM / embedding credentials & rate limits | Phase 01, 03 | Technical owner | ⏳ Pending |
| Vector DB selection & access | Phase 03 | Technical owner | ⏳ Pending |
| Evaluation set with labelled evidence | Phase 04, 06 | Project team / reviewer | ⏳ Pending |
| UX review of the assistant workflow | Phase 08 | Claims/ops representative | ⏳ Pending |
| Security / privacy constraints for logging | Phase 09 | Technical / compliance | ⏳ Pending |

---

## Definition of Done — MVP

The MVP is submission-ready when **all** of the following hold. Anything less is
an incomplete MVP, regardless of how polished the UI is.

- [ ] All **Core** phases (00–09) complete with their exit criteria met
- [ ] Approved corpus ingested; ≥ 95% ingestion success
- [ ] 100% of indexed chunks carry document ID, section, and page
- [ ] `POST /ask` returns answer + citations + warnings as JSON
- [ ] `POST /documents/upload` is access-key protected and retrievable ≤ 5 min
- [ ] Golden set run with all six PRD §5 metrics reported
- [ ] Retrieval relevance ≥ 85%
- [ ] Citation support ≥ 90%; citation resolution **100%**
- [ ] Grounded answer rate ≥ 90%
- [ ] Uncertainty handling ≥ 90%, with zero false-confidence answers on
      insufficient-evidence questions
- [ ] P95 latency ≤ 10 s in the deployed environment
- [ ] Every version-conflict question cites the applicable version or raises a
      conflict warning
- [ ] `GET /chunks/{id}` backs the evidence-verification view
- [ ] Logs contain no claim details or personal data
- [ ] Setup, env vars, ingestion, retrieval, evaluation, API, and deployment
      documentation complete (FR-20)
- [ ] Risks, assumptions, and PRD §16 pre-submission gates addressed

---

## Sprint 2 Module Tracker

> The full module list is maintained here as modules are confirmed.

| # | Module | Phase | Status |
|---|---|---|---|
| — | _Modules to be added as confirmed_ | — | ⬜ Not started |

---

## Related

- [PRD](PRD.md) — product scope and requirements
- [UX](UX.md) — screens, flows, states
- [SPEC](SPEC.md) — architecture and domain types
- [API](API.md) — endpoint contracts
- [EVALUATION](EVALUATION.md) — metrics and harness
- [DEPLOYMENT](DEPLOYMENT.md) — setup and runbook
- [../AGENTS.md](../AGENTS.md) — engineering contract
