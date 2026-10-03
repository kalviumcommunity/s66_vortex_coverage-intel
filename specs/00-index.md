# Spec Index

Numbered build contracts. **These are authoritative for implementation.** Code
must not diverge from them; behaviour changes update the matching spec first
(see [`../AGENTS.md`](../AGENTS.md) §6).

| Spec | Covers | PRD refs |
|---|---|---|
| [01 — User Stories & Acceptance](01-user-stories-and-acceptance.md) | US-01..US-07 with testable acceptance criteria | §6 |
| [02 — Functional Requirements](02-functional-requirements.md) | FR-01..FR-20 → module mapping and verification method | §8 |
| [03 — Data Model](03-data-model.md) | `SourceDocument`, `Chunk`, `RetrievedEvidence`, `Citation`, `Warning`, `CoverageAnswer` | §4, §9 |
| [04 — Ingestion & Chunking](04-ingestion.md) | Loading, extraction, cleaning, chunking, metadata, corpus validation | FR-01..FR-05 |
| [05 — Retrieval](05-retrieval.md) | Embedding, indexing, top-K, hybrid, metadata filters, reranking | FR-06..FR-10 |
| [06 — Generation & Guardrails](06-generation-and-guardrails.md) | Context assembly, grounded generation, citations, guardrails, applicability | FR-11..FR-14 |
| [07 — API Contract](07-api-contract.md) | Endpoint, schema, and error contracts | FR-15, FR-16 |
| [08 — Evaluation Contract](08-evaluation.md) | Metric definitions, golden set rules, re-eval triggers | FR-18, §5 |
| [09 — Open Questions & Blockers](09-open-questions.md) | Unresolved decisions and external blockers | §10.1, §11 |

## Status Legend

| Marker | Meaning |
|---|---|
| ⬜ | Not started |
| 🟡 | In progress |
| ✅ | Complete and verified |
| ⛔ | Blocked on an external dependency |
| 🔵 | Optional / recommended — not MVP-gating |

## Reading Order

1. Start with **[03 — Data Model](03-data-model.md)** — everything else depends on it.
2. Then **[02 — Functional Requirements](02-functional-requirements.md)** for scope.
3. Then the module spec for the phase you are in.
4. Check **[09 — Open Questions](09-open-questions.md)** before making a
   precedence, threshold, or corpus decision — several are awaiting external
   confirmation.
