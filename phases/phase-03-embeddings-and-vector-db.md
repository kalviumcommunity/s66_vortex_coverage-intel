# Phase 03 — Embeddings & Vector Database

**LUs:** 3.25–3.27, 3.30–3.34 (Core) · **Status:** ⬜ Blocked on Q-04, Q-05
**Spec:** [05](../specs/05-retrieval.md)

---

## Scope

Vectors in, searchable index out, with metadata filtering and hybrid retrieval.

## Tasks

- [ ] Confirm embedding provider (Q-04) and vector DB (Q-05)
- [ ] `embeddings/encoder.py` — `Embedder` protocol + implementation
- [ ] `vectorstore/index.py` — `VectorStore` protocol; Chroma adapter (dev)
- [ ] Qdrant adapter (prod) behind the same interface
- [ ] `retrieval/semantic.py` — top-K with scores and metadata
- [ ] `retrieval/keyword.py` — BM25 index
- [ ] `retrieval/hybrid.py` — α fusion, configurable
- [ ] Metadata filters: category, version, jurisdiction, effective date, endorsement link
- [ ] `scripts/index.py`; idempotent upsert; `delete_by_document`
- [ ] Re-index path on model/dimension change

## Exit Criteria

- [ ] Embeddings generated with the configured model; dimensions consistent
- [ ] Index round-trips: upsert → search → `get_chunk`
- [ ] `delete_by_document` removes all chunks and vectors
- [ ] Top-5 retrieval returns score **and** metadata
- [ ] Filters demonstrably exclude non-matching chunks
- [ ] Effective-date filter resolves the version in effect on `date_of_loss`
- [ ] Hybrid ≥ dense-only on `recall@5`
- [ ] No provider SDK import outside the interface implementations
- [ ] Swapping Chroma ↔ Qdrant touches no pipeline logic

## Blockers

| Blocker | Owner |
|---|---|
| Q-04 — embedding access | Technical owner |
| Q-05 — vector DB selection | Technical owner |
