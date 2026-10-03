# 05 — Retrieval Contract

Traceability: FR-06..FR-10 · [PRD §9](../docs/PRD.md#9-rag-workflow--application-architecture) stages 4, 6, 7 · LU 3.25–3.36

---

## Stage 4 — Embedding & Indexing

### FR-06 — Embeddings

```python
class Embedder(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...
    @property
    def dimensions(self) -> int: ...
```

| Rule | Detail |
|---|---|
| Model | `CI_EMBEDDING_MODEL` — never hardcoded |
| Same model for documents and queries | **Required**; mismatched models produce meaningless scores |
| Dimensionality change | Re-index **everything**, then recalibrate `CI_SIMILARITY_THRESHOLD` |
| Batch size | Configurable; rate-limit aware |

### FR-07 — Indexing

```python
class VectorStore(Protocol):
    def upsert(self, chunks: Sequence[Chunk], vectors: list[list[float]]) -> None: ...
    def search(self, vector: list[float], k: int, filters: MetadataFilter | None) -> list[ScoredChunk]: ...
    def delete_by_document(self, document_id: str) -> None: ...
    def get_chunk(self, chunk_id: str) -> Chunk | None: ...
```

| Field | Vector | Payload (filterable) |
|---|---|---|
| | `list[float]` | `document_id`, `category`, `version`, `effective_from`, `effective_to`, `jurisdiction`, `linked_policy_id`, `section`, `page`, `metadata_incomplete` |

- Upsert is **idempotent** on `chunk_id`.
- `delete_by_document` backs retiring superseded versions — a retired version
  must not stay retrievable as if current.

---

## Stage 6 — Retrieval

### FR-08 — Top-K

**Accept:** top-**5** by default, K configurable, each result carrying similarity
score **and** metadata.

```python
def retrieve(question: str, k: int = 5, filters: MetadataFilter | None = None,
             scenario: Scenario | None = None) -> list[RetrievedEvidence]: ...
```

Every result exposes `semantic_score`, `keyword_score`, `hybrid_score`,
`rerank_score` (when applicable), `rank`, and full chunk metadata.

### FR-09 — Metadata filters + hybrid

**Filters are applied before scoring.**

| Filter | Source |
|---|---|
| `category` | Request |
| `jurisdiction` | Request / scenario |
| `version` | Request |
| `effective_as_of` | `scenario.date_of_loss` |
| `linked_policy_id` | Derived from endorsements in evidence |

> **Effective-date filter semantics:** `effective_from ≤ date_of_loss ≤ effective_to`,
> where `effective_to is None` means *open-ended*. A chunk **outside** its period
> is **not silently discarded** if it is the strongest match — it is returned
> with a `SUPERSEDED_VERSION` flag so the conflict is visible (FR-14, US-04).

**Hybrid scoring**

```
score_hybrid = α · score_dense + (1 − α) · score_sparse     # α = CI_HYBRID_ALPHA, default 0.7
```

Policy language is lexically specific (defined terms, clause numbers), so
keyword retrieval carries real signal that pure semantic search drops.
Reciprocal Rank Fusion is the documented alternative when dense and sparse score
distributions are not comparable.

| Rule | Detail |
|---|---|
| α configurable | Yes — swept during Phase 04 |
| Sparse index | BM25 over `chunk.text` |
| Scores normalised | Before fusion; raw cosine and BM25 are not on a shared scale |

### Stage 7 — Reranking (LU 3.35, **Recommended**)

```python
class Reranker(Protocol):
    def rerank(self, query: str, evidence: list[RetrievedEvidence], k: int) -> list[RetrievedEvidence]: ...
```

- Optional. Disabled by default (`CI_RERANK_ENABLED=false`).
- Reranks the top `CI_RERANK_TOP_N` (default 20) candidates down to final K.
- **Enabled or not, retrieval must meet recall@5 ≥ 85% on its own.**

---

## Query Understanding

```python
class Scenario(BaseModel):
    policy_type: str | None = None
    date_of_loss: date | None = None
    jurisdiction: str | None = None
    claim_type: str | None = None
```

`date_of_loss` drives version resolution (US-04). When absent, version
applicability cannot be asserted and a warning is emitted — the system does not
assume "current version".

---

## FR-10 — Retrieval Evaluation

```python
scripts/evaluate.py --suite golden --stage retrieval
```

| Metric | Target |
|---|---|
| `recall@5` | ≥ 0.85 |
| Per-category recall | Reported |
| Misses with rank | Listed — this is the tuning work queue |

**Tuning order** — stop at the first change that clears the target:

1. Chunk size / overlap
2. `α` (dense vs. sparse weight)
3. Top-K for the candidate pool
4. Metadata filters (add `effective_as_of`, `jurisdiction`)
5. Reranking

> Tuning uses `evals/dev/` **only**. `evals/golden/` is never tuned against.

---

## Interface Isolation

Provider code lives behind `Embedder`, `VectorStore`, `KeywordIndex`, and
`Reranker`. Swapping Chroma → Qdrant or one embedding provider → another must
touch **no** pipeline logic. Enforced by
[`02-functional-requirements.md`](02-functional-requirements.md) module boundaries.

---

## Exit Criteria

- [ ] Embeddings generated with the configured model; dimensions consistent
- [ ] Index round-trips: upsert → search → `get_chunk`
- [ ] `delete_by_document` removes all chunks and vectors
- [ ] Top-5 retrieval returns score **and** metadata
- [ ] Metadata filters demonstrably exclude non-matching chunks
- [ ] Effective-date filter resolves the version in effect on `date_of_loss`
- [ ] Hybrid retrieval improves or matches dense-only on `recall@5`
- [ ] `recall@5` ≥ 0.85 on the dev suite
- [ ] Reranking is toggleable and the core path works with it **off**
- [ ] No provider SDK import outside the interface implementations
