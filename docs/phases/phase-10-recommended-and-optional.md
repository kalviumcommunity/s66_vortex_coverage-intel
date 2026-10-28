# Phase 10 — Recommended & Optional Capabilities

**LUs:** 3.29, 3.35, 3.42, 3.47 (streaming), 3.48 · **Status:** ⬜ Additive

---

## Scope

**None of this gates the MVP.** Ship the core, then add these if time allows —
each must earn its place by improving a measured metric.

| Capability | LU | Tier | Adds |
|---|---|---|---|
| **Reranking** | 3.35 | Recommended | Cross-encoder reordering of top candidates |
| **Embedding quality checks** | 3.29 | Recommended | Detect poor representations before retrieval degrades |
| **Conversational RAG** | 3.42 | Recommended / Conditional | Follow-ups retain claim context |
| **Streaming generation** | 3.47 | Optional | Incremental token delivery |
| **Caching & monitoring** | 3.48 | Recommended | Repeated-query latency, usage visibility |

## Adoption rules

| Rule | Detail |
|---|---|
| P-1 | Adopt only with a **measured** improvement on a PRD §5 metric |
| P-2 | Re-run the **full** evaluation suite before and after |
| P-3 | A regression in any metric is a rejection, regardless of gains elsewhere |
| P-4 | The core path must work with every one of these **disabled** |
| P-5 | Conversation state is persisted → re-opens the security/privacy review (Q-07) |

## Per-capability notes

### Reranking (3.35)
Reranks the top `CI_RERANK_TOP_N` candidates to final K. Must improve `recall@5`
or citation support to justify its latency cost. **Off by default.**

### Embedding quality checks (3.29)
Detect degenerate representations — near-duplicate embeddings, unexpected
dimensionality, zero-variance vectors, and outliers against the corpus
distribution. Cheap to add, and it catches corpus problems before they silently
degrade every query.

### Conversational RAG (3.42)
Adopt only if Q-10 confirms follow-up questions must retain claim context.
Persistence of conversation state means claim data is stored — **requires the
security reviewer's sign-off** before it ships.

### Streaming (3.47)
UX polish only. **Citation display is not optional** and remains core.

### Caching & monitoring (3.48)
Cache identical query+filters combinations. Cached answers must preserve the
original `query_id`, `warnings`, and citations so a cached response is
indistinguishable from a fresh one to the adjuster — including its staleness
implications when the corpus has since changed.

## Exit Criteria

- [ ] Each adopted capability has a before/after evaluation report
- [ ] No metric regressed
- [ ] Core path verified with all adopted capabilities disabled
- [ ] Q-07 re-reviewed if conversation state is persisted
