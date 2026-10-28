# Phase 08 — Frontend UI

**LUs:** 3.46, 3.47 citation display (Core); streaming (Optional) · **Status:** ⬜ Blocked on UX review
**Spec:** [UX.md](../docs/UX.md) · FR-13, FR-17

---

## Scope

Four surfaces. Citation display is **core**; streaming is not.

## Tasks

- [ ] **Dashboard** — question entry, suggested inquiries, KB search, recent
      investigations, document/chunk metrics, ingestion status, latency, health
- [ ] **Coverage Assistant** — the core flow:
  - [ ] Question + scenario input
  - [ ] Grounded answer with inline citations
  - [ ] Evidence list with document, section, page, version
  - [ ] Warnings as first-class components
  - [ ] Follow-up questions *(conditional — conversational RAG)*
- [ ] **Evidence Viewer** — source document, outline, section/page navigation,
      highlighted passage, match score, grounding rationale, copy excerpt,
      return to assistant
- [ ] **Evaluation & Governance** — metric dashboards, golden cases, expected vs.
      retrieved, trace inspection, citation verification
- [ ] All UI states: `answering`, `grounded`, `weak_evidence`, `conflicting`,
      `no_evidence`, `error`, `superseded`
- [ ] Decision-support notice visible on the assistant surface

## Exit Criteria

- [ ] UX-01..UX-08 acceptance criteria met
- [ ] Every evidence excerpt shows document, section, page — `not available` for
      absent fields
- [ ] Selecting a citation opens the source at the page with the passage highlighted
- [ ] ≥ 90% of exclusion/endorsement/conflict/insufficient questions show a visible warning
- [ ] Version-conflict questions show the applicable version or a conflict warning
- [ ] KB status visible from the dashboard
- [ ] **No screen renders approval, denial, or settlement language** — asserted in tests

## Blockers

| Blocker | Owner |
|---|---|
| UX review of the assistant workflow | Claims / operations representative |
