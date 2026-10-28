# Phase 07 — Backend API & Upload Endpoint

**LUs:** 3.44–3.45 (Core) · **Status:** ⬜
**Spec:** [07](../specs/07-api-contract.md) · [API.md](../docs/API.md)

---

## Scope

Expose the pipeline. Also the runtime path for keeping the knowledge base
current without a rebuild.

## Tasks

- [ ] `api/app.py` — FastAPI app, CORS, error handlers
- [ ] `api/schemas.py` — Pydantic request/response models, OpenAPI generated
- [ ] `api/routes.py`:
  - [ ] `POST /ask`
  - [ ] `POST /documents/upload`
  - [ ] `GET /documents`, `GET /documents/{id}`, `DELETE /documents/{id}`
  - [ ] `GET /chunks/{chunk_id}` — backs evidence verification
  - [ ] `GET /health`, `GET /metrics`
  - [ ] `POST /evaluate`
- [ ] `api/security.py` — `X-Access-Key`, constant-time comparison, never logged
- [ ] Async upload processing with status polling; retrievable ≤ 5 minutes
- [ ] Contract tests for every endpoint and error code

## Exit Criteria

- [ ] `POST /ask` returns answer + citations + warnings, **including on refusal**
- [ ] `status != "grounded"` returns HTTP **200**, not an error
- [ ] Upload without a valid access key → `401`
- [ ] Endorsement without `linked_policy_id` → `422`; bad type → `415`
- [ ] Uploaded document retrievable within **5 minutes**
- [ ] `GET /chunks/{id}` returns full metadata for the evidence view
- [ ] Error envelope consistent; **no partial answers in error responses**
- [ ] Access key never logged or echoed
- [ ] OpenAPI generated from schemas — contract cannot drift from code
- [ ] Tests assert no adjudication language in any response
