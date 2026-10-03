# Technical Specification — Coverage Intel

> Build contracts live in [`specs/`](../specs/). This document is the architecture
> overview and the decisions behind it.

---

## 1. Architecture

```
                     ┌──────────────────────────────────────┐
  Approved sources   │  1. SOURCE INTAKE                   │
  (PDF/DOCX/TXT)  ──▶│     policy / claims / UW / endorse.  │
                     └──────────────┬───────────────────────┘
                                    ▼
                     ┌──────────────────────────────────────┐
                     │  2. EXTRACTION & CLEANING            │
                     │     text extraction, de-boilerplate, │
                     │     whitespace/encoding normalise    │
                     └──────────────┬───────────────────────┘
                                    ▼
                     ┌──────────────────────────────────────┐
                     │  3. CHUNKING & METADATA              │
                     │     section-aware, 500 tok / 50 ovl │
                     │     full provenance metadata         │
                     └──────────────┬───────────────────────┘
                                    ▼
                     ┌──────────────────────────────────────┐
                     │  4. EMBEDDING & INDEXING             │
                     │     vectors + metadata in vector DB  │
                     └──────────────┬───────────────────────┘
                                    │
   ┌────────────────────────────────▼─────────────────────────────────┐
   │ 5. QUERY UNDERSTANDING — scenario + question, applicability ctx │
   └────────────────────────────────┬─────────────────────────────────┘
                                    ▼
                     ┌──────────────────────────────────────┐
   query ──────────▶│ 6. RETRIEVAL                           │
                     │     semantic ∥ keyword, metadata filter│
                     └──────────────┬───────────────────────┘
                                    ▼
                     ┌──────────────────────────────────────┐
                     │ 7. RERANKING (optional / recommended)│
                     └──────────────┬───────────────────────┘
                                    ▼
                     ┌──────────────────────────────────────┐
                     │ 8. APPLICABILITY & CONFLICT ANALYSIS  │
                     │     version, effective period, juris- │
                     │     diction, endorsement, authority   │
                     └──────────────┬───────────────────────┘
                                    ▼
                     ┌──────────────────────────────────────┐
                     │ 9. CONTEXT ASSEMBLY (bounded, ids)   │
                     └──────────────┬───────────────────────┘
                                    ▼
                     ┌──────────────────────────────────────┐
                     │ 10. GROUNDED GENERATION (T ≤ 0.2)    │
                     └──────────────┬───────────────────────┘
                                    ▼
                     ┌──────────────────────────────────────┐
                     │ 11. CITATIONS & GUARDRAILS           │
                     │     refuse on weak/conflicting evidence│
                     └──────────────┬───────────────────────┘
                                    ▼
                     ┌──────────────────────────────────────┐
                     │ 12. PRESENTATION & LOGGING           │
                     │     API → UI, structured logs         │
                     └──────────────────────────────────────┘
```

---

## 2. Core Domain Types

### 2.1 `SourceDocument`

Registered at ingestion. One per ingested file.

```python
class SourceCategory(StrEnum):
    POLICY = "policy"
    CLAIM_GUIDELINE = "claim_guideline"
    UNDERWRITING_MANUAL = "underwriting_manual"
    ENDORSEMENT = "endorsement"
    APPROVED_REFERENCE = "approved_reference"

class SourceDocument(BaseModel):
    document_id: str                 # stable, unique, derived from filename + content hash
    title: str
    category: SourceCategory
    file_type: Literal["pdf", "docx", "txt"]
    version: str | None              # None -> chunk flagged metadata_incomplete
    effective_from: date | None
    effective_to: date | None        # None == open-ended, not missing
    jurisdiction: str | None
    authority_rank: int | None       # higher wins when precedence is defined
    linked_policy_id: str | None     # required for ENDORSEMENT
    checksum: str
    ingested_at: datetime
```

> `effective_to = None` means "still in effect". It is distinct from *unknown*.
> Unknown is represented by `effective_from = None` **plus**
> `metadata_incomplete = True`.

### 2.2 `Chunk`

```python
class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    section: str | None              # section-aware chunking
    page: int | None
    token_count: int
    char_start: int | None           # offset back into extracted doc
    char_end: int | None

    # inherited provenance
    category: SourceCategory
    version: str | None
    effective_from: date | None
    effective_to: date | None
    jurisdiction: str | None
    linked_policy_id: str | None

    metadata_incomplete: bool = False   # missing version or effective date
    missing_fields: list[str] = []      # for the "not available" rendering
```

**Invariant:** `document_id`, `chunk_id` always present. `section` and `page`
always present or explicitly `None` → rendered `not available`.

### 2.3 `RetrievedEvidence`

```python
class RetrievedEvidence(BaseModel):
    chunk: Chunk
    semantic_score: float            # cosine similarity, 0..1
    keyword_score: float | None
    hybrid_score: float              # fused, used for ordering
    rerank_score: float | None       # populated when reranking enabled
    rank: int
    retrieval_trace_id: str
```

### 2.4 `Citation`

```python
class Citation(BaseModel):
    citation_index: int              # [1], [2] as displayed
    chunk_id: str
    document_id: str
    document_title: str
    section: str | None
    page: int | None
    version: str | None
    effective_from: date | None
    effective_to: date | None
    jurisdiction: str | None
    excerpt: str                     # verbatim span, never paraphrased
```

### 2.5 `Warning`

```python
class WarningKind(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LOW_SIMILARITY = "low_similarity"
    CONFLICTING_SOURCES = "conflicting_sources"
    VERSION_CONFLICT = "version_conflict"
    SUPERSEDED_VERSION = "superseded_version"
    ENDORSEMENT_APPLIES = "endorsement_applies"
    EXCLUSION_FOUND = "exclusion_found"
    METADATA_INCOMPLETE = "metadata_incomplete"
    REVIEW_REQUIRED = "review_required"

class Warning(BaseModel):
    kind: WarningKind
    severity: Literal["info", "warning", "blocking"]
    message: str
    chunk_ids: list[str] = []
    detail: dict[str, Any] = {}
```

### 2.6 `CoverageAnswer`

```python
class AnswerStatus(StrEnum):
    GROUNDED = "grounded"                  # evidence supports a position
    WEAK_EVIDENCE = "weak_evidence"        # below threshold -> review required
    CONFLICTING = "conflicting"            # sources disagree
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"

class AnswerStatement(BaseModel):
    text: str
    citation_indices: list[int]           # must be non-empty for GROUNDED

class CoverageAnswer(BaseModel):
    query_id: str
    question: str
    status: AnswerStatus
    summary: str                          # never adjudicates
    statements: list[AnswerStatement]
    citations: list[Citation]
    warnings: list[Warning]
    evidence: list[RetrievedEvidence]
    generated_at: datetime
    latency_ms: int
    stages: dict[str, int]                # per-stage latency
```

---

## 3. Interfaces

Provider code lives behind these. Nothing provider-specific leaks into the
pipeline.

```python
class DocumentLoader(Protocol):
    def load(self, path: Path) -> ExtractedDocument: ...

class Embedder(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...
    @property
    def dimensions(self) -> int: ...

class VectorStore(Protocol):
    def upsert(self, chunks: Sequence[Chunk], vectors: list[list[float]]) -> None: ...
    def search(self, vector: list[float], k: int, filters: MetadataFilter | None) -> list[ScoredChunk]: ...
    def delete_by_document(self, document_id: str) -> None: ...
    def get_chunk(self, chunk_id: str) -> Chunk | None: ...

class KeywordIndex(Protocol):
    def search(self, query: str, k: int, filters: MetadataFilter | None) -> list[ScoredChunk]: ...

class Reranker(Protocol):
    def rerank(self, query: str, evidence: list[RetrievedEvidence], k: int) -> list[RetrievedEvidence]: ...

class LLMClient(Protocol):
    def generate_structured(self, prompt: str, schema: type[T], temperature: float) -> T: ...
```

---

## 4. Key Algorithms

### 4.1 Section-aware, token-aware chunking (FR-04)

1. Extract text **with structural markers** (`## section`, page breaks).
2. Split into sections at detected headings; fall back to a single synthetic
   section when none are detected — never silently drop the hierarchy.
3. Within each section, pack sentences into chunks of **500 tokens** with
   **50-token overlap**, configurable.
4. Never merge across a section boundary unless a single section is smaller than
   the chunk size, in which case merge forward and record both section labels.
5. A chunk spanning pages records the page range `first–last`.

### 4.2 Cleaning (FR-03)

Removes: repeated headers/footers (detected by line-frequency across pages),
standalone page numbers, watermarks, bullet glyph noise.
**Preserves:** numbered clause references (`Section 7.2`), defined terms, policy
sentence structure. Cleaning that destroys a clause reference is a bug.

### 4.3 Hybrid retrieval (FR-08, FR-09)

```
score_dense  = cosine(embed(q), embed(chunk))          # vector store
score_sparse = BM25(q, chunk_text)                      # keyword index
score_hybrid = α · score_dense + (1 − α) · score_sparse  # α default 0.7
```

Reciprocal Rank Fusion is the documented alternative when dense and sparse score
distributions are not comparable. α is configurable and recorded in eval runs.

**Metadata filters applied before scoring:** `category`, `version`,
`effective_from ≤ date_of_loss ≤ effective_to`, `jurisdiction`,
`linked_policy_id`.

### 4.4 Applicability & conflict analysis (9.1)

Applied to the retrieved evidence **before** context assembly.

```
1. ENDORSEMENT   linked_policy_id → supersede the base policy chunk
2. VERSION       effective_from ≤ date_of_loss ≤ effective_to, else flag SUPERSEDED_VERSION
3. JURISDICTION  if question names a jurisdiction, prefer matching; mismatches are flagged
4. CONFLICT      same topic + differing normative statement + no resolvable
                 precedence → CONFLICTING_SOURCES, human review required
5. EXCLUSION     detection of exclusion/clause language → EXCLUSION_FOUND warning
```

Precedence is resolved **only** from validated metadata. Never from similarity
score.

### 4.5 Guardrails (FR-14)

Evaluated **before** generation, in order. The first trigger wins.

| # | Condition | Outcome |
|---|---|---|
| 1 | No evidence retrieved | `INSUFFICIENT_EVIDENCE` |
| 2 | `top_semantic_score < SIMILARITY_THRESHOLD` | `WEAK_EVIDENCE` + `LOW_SIMILARITY` warning |
| 3 | No chunk scores above `RELEVANCE_FLOOR` | `INSUFFICIENT_EVIDENCE` |
| 4 | Unresolved conflict detected | `CONFLICTING` + `REVIEW_REQUIRED` |
| 5 | All supporting chunks `metadata_incomplete` | `WEAK_EVIDENCE` + `METADATA_INCOMPLETE` |

When any trigger fires, generation is **skipped or constrained** and an explicit
uncertainty/review response is returned. The system never degrades to an
unevidenced answer.

### 4.6 Context assembly (FR-11)

- Budget = `min(MAX_CONTEXT_TOKENS, model_context_limit − reserve_for_output)`.
- Evidence ordered by final score, packed until the budget is exhausted.
- Every evidence block carries its citation index and full provenance header.
- Truncation is recorded in `stages` so the UI can say evidence was limited.

---

## 5. Configuration

All tunables are environment-driven via `src/coverage_intel/config.py`
(Pydantic settings). Defaults follow the PRD; nothing is hardcoded at call sites.

| Variable | Default | Purpose |
|---|---|---|
| `CI_CHUNK_SIZE_TOKENS` | `500` | FR-04 |
| `CI_CHUNK_OVERLAP_TOKENS` | `50` | FR-04 |
| `CI_TOP_K` | `5` | FR-08 |
| `CI_HYBRID_ALPHA` | `0.7` | FR-09 dense weight |
| `CI_SIMILARITY_THRESHOLD` | `0.35` | FR-14 refusal threshold — **must be calibrated on the golden set, not guessed** |
| `CI_RELEVANCE_FLOOR` | `0.30` | FR-14 |
| `CI_GENERATION_TEMPERATURE` | `0.2` | FR-12 max |
| `CI_MAX_CONTEXT_TOKENS` | `6000` | FR-11 |
| `CI_RERANK_ENABLED` | `false` | LU 3.35 |
| `CI_RERANK_TOP_N` | `20` | Candidates fed to reranker |
| `CI_EMBEDDING_MODEL` | — | FR-06 |
| `CI_LLM_MODEL` | — | FR-12 |
| `CI_VECTOR_STORE` | `chroma` | `chroma` \| `qdrant` |
| `CI_UPLOAD_ACCESS_KEY` | — | FR-16, required |
| `CI_LOG_LEVEL` | `INFO` | FR-19 |

> ⚠️ `CI_SIMILARITY_THRESHOLD` is score-distribution dependent and changes when
> the embedding model changes. It must be recalibrated on the golden set, never
> copied between models. This is a tracked open decision — see `specs/09-...`.

---

## 6. Logging (FR-19)

Structured JSON, one line per query.

```json
{
  "query_id": "q_01J...",
  "timestamp": "2026-01-01T00:00:00Z",
  "filters": {"category": null, "jurisdiction": null},
  "retrieved_chunk_ids": ["c_a1b2", "c_c3d4"],
  "answer_status": "grounded",
  "warnings": ["exclusion_found"],
  "latency_ms": {"retrieval": 310, "rerank": 120, "generation": 2400, "total": 2830},
  "error": null
}
```

**Never logged:** question text containing claim details, policy numbers, names,
or any personal data. Chunk *IDs* are logged; chunk *text* is not.

---

## 7. Error Model

| Error | HTTP | Meaning |
|---|---|---|
| `RetrievalError` | 503 | Vector store or keyword index unavailable |
| `GenerationError` | 502 | LLM provider failed or returned unparseable output |
| `UnauthorizedUpload` | 401 | Missing or invalid access key (FR-16) |
| `UnsupportedDocumentType` | 415 | Not PDF/DOCX/TXT |
| `CorpusValidationError` | 422 | Document missing required traceability metadata |
| `GuardrailRefusal` | 200 | **Not an error** — a valid insufficient-evidence response |

`GuardrailRefusal` returns HTTP 200 with `status != GROUNDED`. A refusal is a
correct answer, not a failure.

---

## 8. Key Decisions

| ID | Decision | Rationale | Status |
|---|---|---|---|
| D-01 | Chroma in dev, Qdrant in prod | Zero-setup local dev; production metadata filtering and scaling | Provisional |
| D-02 | Endorsement overrides base policy; version in effect on date of loss applies | PRD §9.1 provisional rule | **Awaiting knowledge-owner confirmation** |
| D-03 | Guardrails run *before* generation | A refusal must not spend an LLM call to discover it cannot answer | Accepted |
| D-04 | Similarity threshold is calibrated, not assumed | Score distributions differ per embedding model | Accepted |
| D-05 | Refusals return HTTP 200 | A refusal is a product-correct outcome | Accepted |
| D-06 | Hybrid retrieval with α=0.7 dense | Policy language is lexically specific; α tunable | Provisional — needs eval |
| D-07 | No conversational context in MVP core | Single-turn is sufficient; conversational RAG is conditional (LU 3.42) | Accepted |

Full ADRs live under `docs/adr/` as they are written.
