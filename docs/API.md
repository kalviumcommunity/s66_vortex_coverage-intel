# API Contract — Coverage Intel

> Implements FR-15, FR-16. Base URL `/api/v1`. All responses are JSON.
> Interactive docs at `/docs` (OpenAPI), redoc at `/redoc`.

---

## Authentication

| Surface | Auth | Notes |
|---|---|---|
| `POST /ask` | **None** | Adjusters are assumed to be on the corporate network; SSO is out of MVP scope. Access logging applies. |
| `POST /documents/upload` | **Required** | `X-Access-Key` header must equal `CI_UPLOAD_ACCESS_KEY` |
| `GET /documents`, `/health`, `/metrics` | None / admin | Introspection endpoints |

> ⚠️ SSO, RBAC, and per-user audit are **out of MVP scope** and flagged for the
> security/privacy reviewer (PRD §11).

---

## `POST /ask`

Ask a coverage question grounded in the approved knowledge base.

### Request

```json
{
  "question": "Is water damage from a burst pipe covered under the HO-3?",
  "scenario": {
    "policy_type": "HO-3",
    "date_of_loss": "2025-03-14",
    "jurisdiction": "CA",
    "claim_type": "water_damage"
  },
  "top_k": 5,
  "filters": {
    "category": ["policy", "endorsement"],
    "jurisdiction": "CA"
  },
  "conversation_id": null
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `question` | string | ✅ | The coverage question |
| `scenario` | object | ⬜ | Supplies applicability context; `date_of_loss` drives version resolution |
| `top_k` | int | ⬜ | Default `CI_TOP_K` (5), clamped to `1..20` |
| `filters` | object | ⬜ | Hard filters applied pre-scoring |
| `conversation_id` | string | ⬜ | Only used when conversational RAG is enabled (LU 3.42) |

### Response `200`

```json
{
  "query_id": "q_01JQ8Z...",
  "question": "Is water damage from a burst pipe covered under the HO-3?",
  "status": "grounded",
  "summary": "The retrieved policy language addresses sudden and accidental water damage from a burst pipe, subject to the conditions listed below. Two exclusions appear relevant and require review before a coverage position is communicated.",
  "statements": [
    {
      "text": "Section I, Coverages, Property Damage covers the loss described.",
      "citation_indices": [1]
    },
    {
      "text": "Flood is excluded from this coverage.",
      "citation_indices": [2]
    }
  ],
  "citations": [
    {
      "citation_index": 1,
      "chunk_id": "c_a1b2c3",
      "document_id": "POL-HO3-2024",
      "document_title": "Homeowners HO-3 Policy Wording",
      "section": "Section I – Coverages",
      "page": 12,
      "version": "2024.1",
      "effective_from": "2024-01-01",
      "effective_to": null,
      "jurisdiction": "CA",
      "excerpt": "We will pay for direct and accidental loss to the property described..."
    }
  ],
  "warnings": [
    {
      "kind": "exclusion_found",
      "severity": "warning",
      "message": "Exclusion language detected in the retrieved evidence.",
      "chunk_ids": ["c_a1b2c3"],
      "detail": {}
    }
  ],
  "evidence": [
    {
      "chunk_id": "c_a1b2c3",
      "document_id": "POL-HO3-2024",
      "section": "Section I – Coverages",
      "page": 12,
      "semantic_score": 0.82,
      "keyword_score": 11.4,
      "hybrid_score": 0.78,
      "rerank_score": 0.91,
      "rank": 1,
      "excerpt": "We will pay for direct and accidental loss..."
    }
  ],
  "stages": {
    "retrieval_ms": 310,
    "rerank_ms": 0,
    "generation_ms": 2410,
    "total_ms": 2834
  },
  "generated_at": "2026-01-01T12:00:00Z"
}
```

### `status` values

| Status | Meaning | UI |
|---|---|---|
| `grounded` | Retrieved evidence supports a stated position | Render answer + evidence |
| `weak_evidence` | Top score below threshold | Uncertainty response + review warning |
| `conflicting` | Authoritative sources disagree, precedence unresolved | Both positions + escalation notice |
| `insufficient_evidence` | No chunk supports the question | Explicit refusal + suggested next step |

> `status != "grounded"` is a **valid answer, not an error**. It returns HTTP 200.

### Response `422` — invalid request

```json
{ "detail": "date_of_loss must be an ISO-8601 date" }
```

---

## `POST /documents/upload`

Add an approved document to the knowledge base at runtime (FR-16, US-07).
Requires `X-Access-Key`.

### Request

`multipart/form-data`

| Part | Type | Required | Notes |
|---|---|---|---|
| `file` | binary | ✅ | `.pdf`, `.docx`, `.txt` — anything else → `415` |
| `document_id` | string | ⬜ | Auto-derived from filename + checksum if omitted |
| `category` | enum | ✅ | `policy` \| `claim_guideline` \| `underwriting_manual` \| `endorsement` \| `approved_reference` |
| `version` | string | ⬜ | |
| `effective_from` | date | ⬜ | |
| `effective_to` | date | ⬜ | |
| `jurisdiction` | string | ⬜ | |
| `linked_policy_id` | string | ⬜ | Required when `category = endorsement` |

### Response `202` — accepted, processing async

```json
{
  "document_id": "POL-HO3-2024",
  "status": "processing",
  "message": "Document accepted for ingestion. Poll GET /documents/{document_id}."
}
```

Target: ingested, embedded, indexed, and **retrievable within 5 minutes** (US-07).

### Responses

| Code | Condition |
|---|---|
| `202` | Accepted |
| `401` | Missing or invalid `X-Access-Key` |
| `413` | File too large |
| `415` | Unsupported file type |
| `422` | Missing required metadata (e.g. `linked_policy_id` for an endorsement) |
| `409` | `document_id` already exists — use the re-index endpoint |

---

## `GET /documents/{document_id}`

Document processing status and index state.

```json
{
  "document_id": "POL-HO3-2024",
  "title": "Homeowners HO-3 Policy Wording",
  "category": "policy",
  "version": "2024.1",
  "effective_from": "2024-01-01",
  "effective_to": null,
  "jurisdiction": "CA",
  "authority_rank": null,
  "linked_policy_id": null,
  "ingestion_status": "indexed",
  "chunk_count": 214,
  "metadata_complete": true,
  "missing_fields": [],
  "ingested_at": "2026-01-01T10:00:00Z",
  "checksum": "sha256:…"
}
```

`ingestion_status`: `pending` → `extracting` → `chunking` → `embedding` → `indexed` | `failed`

---

## `GET /documents`

List registered documents. Supports `?category=`, `?status=`, `?limit=`, `?offset=`.
Powers the dashboard's knowledge-base panel.

---

## `DELETE /documents/{document_id}`

Remove a document and its chunks from the index. Requires `X-Access-Key`.
Used to retire superseded versions — a superseded version must not remain
retrievable as if it were current.

---

## `GET /chunks/{chunk_id}`

Full chunk record with complete metadata — backs the evidence-verification view.
Returns `404` if the chunk is not in the index, which is what makes the
"100% of citations resolve to a real source" metric checkable.

---

## `GET /health`

```json
{
  "status": "healthy",
  "vector_store": "connected",
  "llm": "reachable",
  "documents": 128,
  "chunks": 18422,
  "last_ingestion_at": "2026-01-01T10:00:00Z",
  "p95_latency_ms": 4120
}
```

---

## `GET /metrics`

Prometheus-format retrieval and generation latency, query counts by answer status,
warning counts by kind. **Contains no claim content.**

---

## `POST /evaluate`

Trigger the evaluation suite over the golden set (FR-18). Admin only.

```json
{ "suite": "golden", "compare_to_baseline": true }
```

Returns per-metric results with pass/fail against the PRD §5 targets.

---

## Error Envelope

```json
{
  "error": "GenerationError",
  "message": "LLM provider returned an unparseable structured response.",
  "query_id": "q_01JQ8Z...",
  "retryable": true
}
```

An error **never** returns a partial answer that could be mistaken for a grounded
coverage position.

---

## Conformance Checklist

| Requirement | Endpoint | Status |
|---|---|---|
| FR-15 QA endpoint returning answer + citations + warnings | `POST /ask` | ✅ |
| FR-15 Upload endpoint | `POST /documents/upload` | ✅ |
| FR-16 Access-key-protected runtime indexing | `X-Access-Key` + `401` | ✅ |
| FR-13 Citations with document + section/page | `citations[]`, `GET /chunks/{id}` | ✅ |
| FR-14 Uncertainty/review responses | `status`, `warnings[]` | ✅ |
| US-07 Upload retrievable ≤ 5 min | async status polling | ✅ |
