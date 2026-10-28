# 09 — Open Questions & Blockers

Items that **cannot** be resolved by code alone. Each needs a named owner and an
explicit decision before the dependent phase can pass its exit criteria.

Per [`../AGENTS.md`](../AGENTS.md) §9: if something here affects the design,
**ask** — do not invent a policy.

---

## A. Blocking — External Approval

| # | Question | Blocks | Owner | Status |
|---|---|---|---|---|
| **Q-01** | What is the **approved representative corpus**? | Phase 02+ | Knowledge owner | ⏳ Pending |
| **Q-02** | Which document categories are **authoritative**, and what is the **precedence rule** when they overlap? | Phase 04, 05 | Knowledge / UW / compliance | ⏳ Pending |
| **Q-03** | Is **version, effective date, jurisdiction, section/page, endorsement** metadata actually available in the sources, or must the project add it during ingestion? | Phase 02, 03 | Knowledge owner | ⏳ Pending |
| **Q-04** | Which LLM / embedding provider, at what rate limits and quota? | Phase 01, 03 | Technical owner | ⏳ Pending |
| **Q-05** | Vector DB confirmed — Chroma dev → Qdrant prod, or another choice? | Phase 03 | Technical owner | ⏳ Pending |
| **Q-06** | Who approves the **labelled evaluation set** and its evidence labels? | Phase 04, 06 | Project team / reviewer | ⏳ Pending |
| **Q-07** | Logging and document-handling constraints — retention, PII scope, access? | Phase 09 | Technical / compliance | ⏳ Pending |

> Until Q-01 and Q-03 are answered, all retrieval and applicability numbers are
> provisional. They must be reported as such.

---

## B. Design Decisions — Provisional, Need Confirmation

| # | Decision | Current stance | Risk if wrong |
|---|---|---|---|
| **D-01** | Vector store: Chroma (dev) → Qdrant (prod) | Behind `VectorStore` interface | Low — swappable, but Qdrant metadata-filter semantics must match |
| **D-02** | **Endorsement overrides base policy; version in effect on date of loss applies** | PRD §9.1 provisional rule | **High** — wrong precedence produces confidently wrong coverage |
| **D-03** | Guardrails run **before** generation | Accepted | Low — only a small latency cost |
| **D-04** | Similarity threshold is **calibrated**, never assumed | Accepted | Medium — a stale threshold causes mass false refusals |
| **D-05** | Refusals return HTTP 200 | Accepted | Low |
| **D-06** | Hybrid α = 0.7 dense | Provisional | Low — tunable, eval-driven |
| **D-07** | No conversational context in MVP core | Accepted | Medium if follow-ups turn out to be a real workflow |

**D-02 is the highest-risk item in the project.** It defines which document wins,
and it is currently a *provisional* rule awaiting knowledge-owner confirmation.

---

## C. Product Ambiguities

| # | Question | Current handling |
|---|---|---|
| **Q-08** | What exactly is a "coverage assessment" the adjuster wants — a determination, or a summary of what the policy language says? | MVP renders **evidence**, not a determination. Adjudication is out of scope (PRD §7.2) |
| **Q-09** | When two clauses are both applicable but imply different outcomes, is that a *conflict* (→ human review) or *conditions stacking*? | Treated as conflict unless precedence is derivable — deliberately conservative |
| **Q-10** | Does a follow-up question need to retain claim context? | Decides whether conversational RAG (LU 3.42) is conditional or required |
| **Q-11** | Are scanned/image PDFs in the real corpus? | OCR is out of MVP scope. If yes, scope changes materially — raise before Phase 02 |
| **Q-12** | Should the adjuster be able to override a guardrail and force an answer? | **No** in MVP. A "show me the raw evidence anyway" action is a UI affordance, not a guardrail bypass |

---

## D. Metrics Needing Business Confirmation

Per PRD §2.2, these **must not be invented**.

| Metric | Status |
|---|---|
| Number of adjusters affected | ⬜ Unverified |
| Current average lookup time | ⬜ Unverified |
| Current misquote rate | ⬜ Unverified |
| Financial impact of misquoting | ⬜ Unverified |
| Baseline misquote rate for post-MVP comparison | ⬜ Unverified — without this, improvement cannot be demonstrated |

> Any presentation of these numbers must be marked **pending validation**.

---

## E. Escalation — Unresolved by Design

Some situations **have no correct automated answer** and the system is expected
to escalate:

1. Two authoritative sources conflict and precedence is undeterminable
2. Retrieved evidence is above threshold but too weak to support a position
3. All supporting chunks carry incomplete metadata
4. An endorsement's relationship to the base policy is ambiguous
5. The question requires judgment outside documented policy language

Each must produce `REVIEW_REQUIRED` — never a best guess.
