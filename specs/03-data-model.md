# 03 — Data Model

Traceability: [PRD §4](../docs/PRD.md#4-knowledge-source-documentation), §9.1.
Full narrative in [SPEC.md §2](../docs/SPEC.md#2-core-domain-types).

All types are **Pydantic v2**. Metadata is never a bare dict.

---

## Invariants

These hold across every stage. A violation is a bug, not a configuration issue.

| # | Invariant | Enforced by |
|---|---|---|
| I-1 | `chunk_id` and `document_id` are **never** `None` | Type system |
| I-2 | `section` and `page` are always present **or explicitly `None`** → rendered `not available` | Type system + UI |
| I-3 | Missing `version` or `effective_from` ⇒ `metadata_incomplete=True` | `Chunk` validator |
| I-4 | `effective_to = None` means *still in effect* — **not** unknown. Unknown is expressed by `metadata_incomplete`. | Convention |
| I-5 | A `Chunk` is **immutable after indexing** | `model_config = ConfigDict(frozen=True)` |
| I-6 | A `Citation` must reference a `chunk_id` present in the index | Eval harness; `GET /chunks/{id}` |
| I-7 | An `AnswerStatement` in a `GROUNDED` answer must carry ≥ 1 citation | Post-generation validator |
| I-8 | No field holds raw claim text or personal data | Code review + log audit |

---

## Enums

```python
class SourceCategory(StrEnum):
    POLICY              = "policy"
    CLAIM_GUIDELINE     = "claim_guideline"
    UNDERWRITING_MANUAL = "underwriting_manual"
    ENDORSEMENT         = "endorsement"
    APPROVED_REFERENCE  = "approved_reference"

class AnswerStatus(StrEnum):
    GROUNDED             = "grounded"
    WEAK_EVIDENCE        = "weak_evidence"
    CONFLICTING          = "conflicting"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"

class WarningKind(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LOW_SIMILARITY        = "low_similarity"
    CONFLICTING_SOURCES   = "conflicting_sources"
    VERSION_CONFLICT      = "version_conflict"
    SUPERSEDED_VERSION    = "superseded_version"
    ENDORSEMENT_APPLIES   = "endorsement_applies"
    EXCLUSION_FOUND       = "exclusion_found"
    METADATA_INCOMPLETE   = "metadata_incomplete"
    REVIEW_REQUIRED       = "review_required"
```

> ⚠️ `AnswerStatus` has **no** `approved` / `denied` / `settled` value. Adding one
> would violate [`../AGENTS.md`](../AGENTS.md) §2 rule 6.

---

## `SourceDocument`

One per ingested file.

| Field | Type | Nullable | Notes |
|---|---|---|---|
| `document_id` | `str` | ❌ | Unique; derived from filename + content checksum |
| `title` | `str` | ❌ | |
| `category` | `SourceCategory` | ❌ | |
| `file_type` | `Literal["pdf","docx","txt"]` | ❌ | Anything else rejected |
| `version` | `str` | ✅ | |
| `effective_from` | `date` | ✅ | |
| `effective_to` | `date` | ✅ | `None` = open-ended |
| `jurisdiction` | `str` | ✅ | |
| `authority_rank` | `int` | ✅ | Higher wins **only when precedence is defined** |
| `linked_policy_id` | `str` | ✅ | **Required** when `category = ENDORSEMENT` |
| `checksum` | `str` | ❌ | Idempotent re-ingest |
| `ingested_at` | `datetime` | ❌ | |

**Validator:** `category == ENDORSEMENT and linked_policy_id is None` → `CorpusValidationError`.

---

## `Chunk`

| Field | Type | Nullable | Notes |
|---|---|---|---|
| `chunk_id` | `str` | ❌ | |
| `document_id` | `str` | ❌ | FK → `SourceDocument` |
| `text` | `str` | ❌ | |
| `section` | `str` | ✅ | Section-aware |
| `page` | `int` | ✅ | |
| `page_end` | `int` | ✅ | Set when a chunk spans pages |
| `token_count` | `int` | ❌ | |
| `char_start` / `char_end` | `int` | ✅ | Offset into extracted text |
| `category` | `SourceCategory` | ❌ | Denormalised for filtering |
| `version` | `str` | ✅ | |
| `effective_from` / `effective_to` | `date` | ✅ | |
| `jurisdiction` | `str` | ✅ | |
| `linked_policy_id` | `str` | ✅ | |
| `metadata_incomplete` | `bool` | ❌ | Default `False` |
| `missing_fields` | `list[str]` | ❌ | Names absent fields |

Metadata is denormalised onto the chunk so vector-store filters never require a
join back to the document record.

---

## `RetrievedEvidence`

```python
class RetrievedEvidence(BaseModel):
    chunk: Chunk
    semantic_score: float          # cosine, 0..1
    keyword_score: float | None
    hybrid_score: float            # used for ordering
    rerank_score: float | None     # when reranking enabled
    rank: int
    retrieval_trace_id: str
```

---

## `Citation`

```python
class Citation(BaseModel):
    citation_index: int
    chunk_id: str
    document_id: str
    document_title: str
    section: str | None
    page: int | None
    version: str | None
    effective_from: date | None
    effective_to: date | None
    jurisdiction: str | None
    excerpt: str                   # verbatim, never paraphrased
```

`excerpt` is copied from the indexed chunk **verbatim** so the adjuster can
verify exact policy wording (UX screen 3). A paraphrase is a defect.

---

## `Warning`

```python
class Warning(BaseModel):
    kind: WarningKind
    severity: Literal["info", "warning", "blocking"]
    message: str
    chunk_ids: list[str] = []
    detail: dict[str, Any] = {}
```

`severity="blocking"` renders as a full-panel state, not a toast.

---

## `CoverageAnswer`

```python
class CoverageAnswer(BaseModel):
    query_id: str
    question: str
    status: AnswerStatus
    summary: str
    statements: list[AnswerStatement]
    citations: list[Citation]
    warnings: list[Warning]
    evidence: list[RetrievedEvidence]
    generated_at: datetime
    latency_ms: int
    stages: dict[str, int]
```

**Post-generation validator (I-7):** if `status == GROUNDED`, every
`AnswerStatement.citation_indices` must be non-empty and every index must exist
in `citations`. A violation downgrades the answer to `WEAK_EVIDENCE` with a
`REVIEW_REQUIRED` warning — it is never emitted as a grounded answer.

---

## `MetadataFilter`

```python
class MetadataFilter(BaseModel):
    category: list[SourceCategory] | None = None
    version: str | None = None
    jurisdiction: str | None = None
    document_ids: list[str] | None = None
    effective_as_of: date | None = None      # date_of_loss
    linked_policy_id: str | None = None
```

`effective_as_of` is what makes FR-09's effective-date filtering meaningful.
It comes from the scenario's `date_of_loss`.

---

## Storage Mapping

| Store | Payload | Notes |
|---|---|---|
| Vector DB — vector | `list[float]` | Provider dimension |
| Vector DB — payload | `Chunk` (minus `text` when large) | Filterable fields flattened |
| Keyword index | `chunk_id`, tokenised `text` | BM25 |
| Relational / manifest | `SourceDocument`, ingestion status | Corpus inventory |
| Transcript (ephemeral) | `CoverageAnswer` | **Not persisted by default**; contains claim context |
