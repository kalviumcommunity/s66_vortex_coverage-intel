# 07 — API Contract

Traceability: FR-15, FR-16 · [Full request/response examples in API.md](../docs/API.md)

This spec is the **normative summary**. `docs/API.md` holds full payloads.

---

## Endpoints

| Method | Path | Auth | FR |
|---|---|---|---|
| `POST` | `/api/v1/ask` | — | FR-15 |
| `POST` | `/api/v1/documents/upload` | `X-Access-Key` **required** | FR-15, FR-16 |
| `GET` | `/api/v1/documents` | — | FR-17 |
| `GET` | `/api/v1/documents/{document_id}` | — | FR-16 |
| `DELETE` | `/api/v1/documents/{document_id}` | `X-Access-Key` | — |
| `GET` | `/api/v1/chunks/{chunk_id}` | — | FR-13 |
| `GET` | `/api/v1/health` | — | — |
| `GET` | `/api/v1/metrics` | — | FR-19 |
| `POST` | `/api/v1/evaluate` | admin | FR-18 |

---

## `POST /ask`

**Request:** `question` (required), `scenario` (optional — supplies
`date_of_loss`, which drives version resolution), `top_k`, `filters`,
`conversation_id`.

**Response `200`:** `query_id`, `status`, `summary`, `statements[]`,
`citations[]`, `warnings[]`, `evidence[]`, `stages{}`, `generated_at`.

### Contract rules

| # | Rule |
|---|---|
| A-1 | Always returns `status`, `citations`, `warnings` — including on refusal |
| A-2 | `status != "grounded"` is a **200**, not an error |
| A-3 | Every `statement.citation_indices` resolves within `citations` |
| A-4 | Every `citation.chunk_id` resolves via `GET /chunks/{chunk_id}` |
| A-5 | Absent metadata fields render `not available` |
| A-6 | `top_k` clamped to `1..20` |
| A-7 | Response language never implies approval, denial, or settlement |

---

## `POST /documents/upload`

| Part | Required | Validation |
|---|---|---|
| `file` | ✅ | `.pdf` / `.docx` / `.txt`, else `415` |
| `category` | ✅ | `SourceCategory` enum |
| `document_id` | ⬜ | Auto-derived if omitted |
| `version`, `effective_from/to`, `jurisdiction` | ⬜ | |
| `linked_policy_id` | conditional | **Required** when `category = endorsement` → else `422` |

| Code | Condition |
|---|---|
| `202` | Accepted; processing is asynchronous |
| `401` | Missing or invalid `X-Access-Key` |
| `409` | `document_id` already exists |
| `413` | File too large |
| `415` | Unsupported type |
| `422` | Missing required metadata |

**SLO:** ingested, embedded, indexed, and **retrievable within 5 minutes**
(US-07).

### Security notes

- The access key is the **only** application-level control in MVP. It must be
  paired with network-level restriction in production.
- Comparison must be constant-time.
- The key is never logged, never echoed in an error, never returned.

---

## `GET /chunks/{chunk_id}`

Returns the full indexed chunk with complete metadata — backs the
evidence-verification view (UX screen 3). `404` when absent; this is what makes
the "100% citation resolution" metric verifiable.

---

## Errors

```json
{ "error": "GenerationError", "message": "...", "query_id": "q_...", "retryable": true }
```

| Error | Code | Note |
|---|---|---|
| `RetrievalError` | 503 | Store/index unavailable |
| `GenerationError` | 502 | LLM failed or returned unparseable output |
| `UnauthorizedUpload` | 401 | Access key invalid |
| `UnsupportedDocumentType` | 415 | |
| `CorpusValidationError` | 422 | Traceability metadata missing |
| `GuardrailRefusal` | **200** | Not an error |

> An error response must **never** carry a partial answer that could be mistaken
> for a grounded coverage position.

---

## OpenAPI

`/docs` (Swagger) and `/redoc` are generated from the Pydantic schemas, so the
contract and the code cannot drift. Any schema change is automatically reflected.

---

## Exit Criteria

- [ ] All endpoints implemented and covered by contract tests
- [ ] `POST /ask` returns answer + citations + warnings, including on refusal
- [ ] `status != "grounded"` returns HTTP 200
- [ ] Upload without a valid access key → `401`
- [ ] Uploaded document retrievable within 5 minutes
- [ ] Endorsement without `linked_policy_id` → `422`
- [ ] `GET /chunks/{id}` backs the evidence view
- [ ] Error envelope consistent; no partial answers in error responses
- [ ] OpenAPI generated from schemas
- [ ] Response payload contains no adjudication language (asserted in tests)
