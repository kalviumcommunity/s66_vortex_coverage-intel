# 01 — User Stories & Acceptance Contract

Traceability: [PRD §6](../docs/PRD.md#6-user-stories--acceptance-indications).

Each story follows **Role + Action + Business Benefit** and has an acceptance
criterion that is *testable* — not "the system should be accurate".

---

## US-01 — Ask a coverage question

> As a claims adjuster, I want to enter a claim scenario and coverage question,
> so that I can locate the relevant policy evidence within ≤ 10 seconds instead
> of searching hundreds of documents manually.

**Acceptance**
- [ ] `POST /api/v1/ask` returns either a grounded answer or an explicit
      insufficient-evidence response
- [ ] P95 end-to-end latency ≤ **10 s**, measured in the deployed environment
- [ ] A refusal is a valid 200 response, not an error

**Verify:** `scripts/evaluate.py --suite golden` → `p95_latency_ms.pass == true`

**Fails when:** the system errors instead of refusing, or exceeds the latency
budget.

---

## US-02 — Retrieve the relevant policy sections

> As a claims adjuster, I want the system to retrieve relevant policy sections,
> so that I do not have to manually search across overlapping documents.

**Acceptance**
- [ ] Supporting chunk appears in **top-5** for ≥ **85%** of evaluation questions
- [ ] Every excerpt shows **document**, **section**, and **page**
- [ ] A field absent from the source renders as `not available` — never blank,
      never guessed

**Verify:** `retrieval_recall_at_5` ≥ 0.85; UI snapshot shows `not available`
for absent fields.

---

## US-03 — Cite the supporting sources

> As a claims adjuster, I want the answer to cite its supporting sources, so
> that I can verify the coverage interpretation against the original document.

**Acceptance**
- [ ] ≥ **90%** of citations support the statement they are attached to
- [ ] **100%** of citations resolve to a real indexed source
- [ ] `GET /api/v1/chunks/{chunk_id}` returns the cited chunk

**Verify:** `citation_support` ≥ 0.90 **and** `citation_resolution` == 1.00.
Resolution is a hard gate, not an average.

---

## US-04 — Consider version and effective date

> As a claims adjuster, I want policy version and effective-date context
> considered, so that an outdated document is not treated as the applicable
> source.

**Acceptance**
- [ ] In **every** `version_conflict` question, the answer cites the version in
      effect on the stated date **or** raises a conflict warning
- [ ] A chunk outside its effective period is never presented as applicable
- [ ] A superseded version is flagged `SUPERSEDED_VERSION`

**Verify:** all 6 `version_conflict` questions pass;
`must_not_be_cited` chunks appear in zero answers.

---

## US-05 — Highlight exclusions and conflicts

> As a claims adjuster, I want exclusions, conditions, endorsements, or
> conflicting evidence highlighted, so that I know when the answer requires
> additional review before I communicate a coverage position.

**Acceptance**
- [ ] ≥ **90%** of exclusion, endorsement, conflict, and insufficient-evidence
      questions display a visible warning
- [ ] Warnings render as first-class UI, not a footnote
- [ ] Message wording never implies approval, denial, or settlement

**Verify:** `warning_coverage` ≥ 0.90 across the relevant categories.

---

## US-06 — Process approved documents with metadata

> As a knowledge owner, I want approved documents to be processed with source
> metadata, so that the retrieval system remains traceable and maintainable.

**Acceptance**
- [ ] **100%** of indexed chunks carry `document_id`, `section`, and `page`
- [ ] `version` and `effective_date` are stored, **or** the chunk is flagged
      `metadata_incomplete` with its missing fields listed
- [ ] Chunks are **never silently dropped** for missing metadata

**Verify:** `metadata_completeness` audit over the full index.

---

## US-07 — Upload an approved document at runtime

> As a knowledge owner, I want to upload an approved document through a
> controlled endpoint, so that the knowledge base stays current without a full
> rebuild.

**Acceptance**
- [ ] Uploaded document is ingested, embedded, indexed, and **retrievable within
      ≤ 5 minutes**
- [ ] A request without a valid `X-Access-Key` is **rejected** with `401`
- [ ] `endorsement` category without `linked_policy_id` → `422`
- [ ] Unsupported file type → `415`

**Verify:** end-to-end upload test + a query that retrieves the new document's
content within 5 minutes.

---

## Traceability Matrix

| Story | FRs | Specs | Phase |
|---|---|---|---|
| US-01 | FR-11..FR-15 | [05](05-retrieval.md), [06](06-generation-and-guardrails.md), [07](07-api-contract.md) | 05, 07 |
| US-02 | FR-08, FR-09 | [05](05-retrieval.md) | 03, 04 |
| US-03 | FR-13 | [06](06-generation-and-guardrails.md), [07](07-api-contract.md) | 05, 07 |
| US-04 | FR-05, FR-09 | [03](03-data-model.md), [05](05-retrieval.md), [06](06-generation-and-guardrails.md) | 02, 05 |
| US-05 | FR-14 | [06](06-generation-and-guardrails.md) | 05 |
| US-06 | FR-01..FR-05 | [04](04-ingestion.md) | 02 |
| US-07 | FR-16 | [07](07-api-contract.md) | 07 |
