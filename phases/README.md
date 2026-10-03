# Phase Plan

Delivery order for Coverage Intel. Overview and LU mapping:
[docs/ROADMAP.md](../docs/ROADMAP.md).

**Rule:** a phase cannot start until the previous phase's exit criteria are met.
Phase 01 and Phase 02 may run in parallel. Phase 10 is independent and additive
at any time.

| Phase | Name | LUs | Tier | Depends on |
|---|---|---|---|---|
| [00](phase-00-foundation.md) | Foundation & Repository | 3.11 | Core | — |
| [01](phase-01-llm-and-prompting.md) | LLM Access & Prompting | 3.12–3.18 | Core | 00 |
| [02](phase-02-ingestion.md) | Ingestion & Chunking | 3.19–3.24 | Core | 00 |
| [03](phase-03-embeddings-and-vector-db.md) | Embeddings & Vector DB | 3.25–3.27, 3.30–3.34 | Core | 02 |
| [04](phase-04-retrieval-tuning.md) | Retrieval Tuning & Eval | 3.36 | Core | 03 |
| [05](phase-05-rag-core.md) | RAG Core & Guardrails | 3.37–3.41 | Core | 04 |
| [06](phase-06-rag-evaluation.md) | RAG Evaluation | 3.43 | Core | 05 |
| [07](phase-07-backend-api.md) | Backend API | 3.44–3.45 | Core | 05 |
| [08](phase-08-frontend-ui.md) | Frontend UI | 3.46–3.47 | Core | 07 |
| [09](phase-09-deployment-and-docs.md) | Deployment & Documentation | 3.49–3.50 | Core | 08 |
| [10](phase-10-recommended-and-optional.md) | Recommended & Optional | 3.29, 3.35, 3.42, 3.47s, 3.48 | Rec./Opt | any |

## Tier Definitions

| Tier | Meaning |
|---|---|
| **Core** | Must ship. The MVP is incomplete without it |
| **Recommended** | Strongly useful, additive. Never blocks core delivery |
| **Optional** | May be skipped entirely |

Skipping **every** Recommended and Optional unit still yields a complete MVP,
provided the required underlying behaviour is implemented.

## Status

⬜ Not started · 🟡 In progress · ✅ Complete · ⛔ Blocked

| Phase | Status | Notes |
|---|---|---|
| 00 | 🟡 | Scaffold complete; awaiting module list |
| 01 | ⬜ | Blocked on Q-04 (LLM access) |
| 02 | ⬜ | Blocked on Q-01, Q-03 (corpus, metadata) |
| 03 | ⬜ | Blocked on Q-04, Q-05 |
| 04 | ⬜ | Blocked on Q-06 (eval set), D-02 |
| 05 | ⬜ | Blocked on D-02 (precedence) |
| 06 | ⬜ | |
| 07 | ⬜ | |
| 08 | ⬜ | Blocked on UX review |
| 09 | ⬜ | Blocked on Q-07 (logging constraints) |
| 10 | ⬜ | |
