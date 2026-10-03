# Phase 02 — Ingestion & Chunking

**LUs:** 3.19–3.24 (Core) · **Status:** ⬜ Blocked on Q-01, Q-03
**Spec:** [04](../specs/04-ingestion.md) · [03](../specs/03-data-model.md)

---

## Scope

Approved documents in, traceable chunks out.

## Tasks

- [ ] Confirm corpus and metadata availability (Q-01, Q-03)
- [ ] `SourceDocument` model + corpus manifest
- [ ] `ingestion/loaders.py` — PDF, DOCX, TXT
- [ ] `ingestion/cleaning.py` — boilerplate removal, whitespace/encoding
- [ ] `ingestion/chunking.py` — section-aware, 500/50 configurable
- [ ] `ingestion/metadata.py` — full provenance; `metadata_incomplete` flag
- [ ] Corpus validation + `scripts/ingest.py --validate`
- [ ] Handle scanned PDFs: fail loudly (OCR is out of scope)
- [ ] Tests per format; clause-reference preservation tests

## Exit Criteria

- [ ] All three formats load with section and page preserved
- [ ] Cleaner removes boilerplate **and** preserves clause references, defined
      terms, negation, and amounts (both asserted by tests)
- [ ] Chunker satisfies invariants C-1..C-5 at default and custom config
- [ ] 100% of chunks carry `document_id`, `section`, `page`
- [ ] Missing version/effective date ⇒ flagged, **not dropped**
- [ ] Endorsements require `linked_policy_id`
- [ ] **Ingestion success ≥ 95%** on the test corpus
- [ ] Validation report generated and reviewed

## Blockers

| Blocker | Owner |
|---|---|
| Q-01 — approved corpus | Knowledge owner |
| Q-03 — metadata availability | Knowledge owner |
| Q-11 — scanned PDFs in corpus? | Knowledge owner |
