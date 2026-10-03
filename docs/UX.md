# UX Specification — Coverage Intel

> Design source: Figma — [Coverage Intel mock UX](https://www.figma.com/design/oeNbHWT7LwOqCIymJnCkhC/mock-UX?node-id=0-1&t=17B9n90GCW2aqQZe-1)

---

## Product Positioning

**Verify Coverage. Ground Every Decision.**

Coverage Intel is an enterprise AI-powered insurance knowledge and coverage
intelligence platform designed to help **authorized insurance personnel** quickly
research policy terms, verify coverage conditions, and trace AI-generated answers
back to approved policy documents.

The platform combines document retrieval, semantic search, reranking, grounded
generation, and citation-based evidence verification to ensure that coverage
answers are supported by the organization's approved insurance knowledge base.

---

## The Four Surfaces

### 1. Coverage Intelligence Dashboard

**Purpose:** the primary workspace for insurance coverage research and
knowledge-base monitoring.

| Content | Detail |
|---|---|
| Coverage question entry | Natural-language question bar with submit |
| Suggested verification inquiries | Curated starter questions per source category |
| Knowledge-base search | Direct document/section search |
| Recent coverage inquiries | Last investigations, resumable |
| Active document & indexed chunk metrics | Counts, per-category breakdown |
| Document ingestion status | Last ingest run, failures, pending |
| Retrieval latency | Current p50 / p95 |
| Knowledge-base health | Composite status with reason |
| Recent evidence-backed investigations | Answer + status + citation count |

**Flow:** land on the dashboard → review knowledge-base status → start an
investigation by entering a question or selecting a suggested inquiry.

---

### 2. Coverage Assistant — Grounded Coverage Research

**Purpose:** the primary AI-assisted coverage research interface. The core
product flow.

| Content | Detail |
|---|---|
| Claim scenario & question input | Optional structured scenario fields + free-text question |
| Natural-language coverage questions | Primary input |
| Conversational follow-up questions | Conditional (conversational RAG) |
| Grounded answer generation | Constrained to retrieved evidence |
| Coverage assessment | **"evidence supports / conflicts / insufficient"** — never "approve / deny" |
| Applicable conditions and exclusions | Surfaced explicitly |
| Inline citations | `[1] [2]` linked to evidence items |
| Retrieved evidence | Excerpts with document, section, page, version |
| Source-document references | Deep-link into evidence viewer |
| Insufficient-evidence handling | Explicit refusal state, not a blank or a guess |
| Follow-up investigation | Refine the question, keep context |

**Flow:**
```
Question → retrieve chunks → metadata filter → rerank → grounded generation
        → attach citations → user inspects evidence
```

---

### 3. Policy Search & Evidence Verification

**Purpose:** a source-verification workspace that connects retrieved evidence to
the original policy document, section, page, and passage.

| Content | Detail |
|---|---|
| Policy/document search | Across indexed approved documents |
| Document outline | Section tree |
| Section navigation | Jump to a specific section |
| Page-level references | Page numbers on every excerpt |
| Highlighted evidence | The exact supporting span |
| Retrieved evidence context | Neighbouring chunks for orientation |
| Semantic match score | Displayed per chunk, with meaning explained |
| Grounding rationale | Why this chunk was retrieved |
| Extracted policy conditions | Structured view of conditions found |
| Cross-referenced clauses | Links to related sections/endorsements |
| Exact excerpt copying | Copy the verbatim policy language |
| Return to assistant | Preserve and return to the active investigation |

**Flow:** select a citation in the assistant → open the source document → the
relevant page and passage are highlighted → verify the exact wording → return to
the coverage investigation.

---

### 4. RAG Evaluation & Governance

**Purpose:** an evaluation and governance workspace used to validate whether the
retrieval and generation pipeline is producing accurate, grounded, and properly
cited insurance answers.

| Content | Detail |
|---|---|
| Retrieval recall | Hit rate against expected documents |
| Citation precision | Citations that support their statement |
| Grounded-answer rate | Unsupported-claim audit |
| Faithfulness / hallucination checks | Per-answer pass/fail |
| Retrieval latency | Stage-level timings |
| Generation latency | Stage-level timings |
| Golden test cases | The labelled evaluation set |
| Expected document comparison | Retrieved vs. expected, side by side |
| Retrieved chunk inspection | Scores, filters, rerank positions |
| Grounding status | Per-question verdict |
| Citation verification | Statement ↔ citation entailment |
| Retrieval trace inspection | Full pipeline trace per query |
| Evidence-level evaluation | Chunk-level outcomes |

**Flow:** run benchmark questions → compare expected documents against retrieved
chunks → inspect retrieval and reranking results → verify generated answers and
citations → investigate discrepancies → validate the RAG pipeline.

---

## Overall User Flow

```
1. Dashboard      — access the coverage workspace, review KB status
2. Question       — enter a natural-language coverage question
3. Grounded Answer— retrieve, rerank, synthesise evidence into a grounded response
4. Verification   — inspect retrieved clauses, citations, exact policy language
5. Resolution     — verify applicable conditions; follow up or escalate for
                    manual review when evidence is insufficient
```

---

## UX Principles

1. **Evidence is never hidden.** Every answer statement is traceable to a visible
   citation. No citation → no claim.
2. **Warnings are first-class UI, not a footnote.** Insufficient evidence,
   conflicting documents, missing metadata, and review-required states render as
   prominent, structured components.
3. **Never present adjudication.** Coverage status uses evidence language —
   *"evidence supports"*, *"evidence conflicts"*, *"insufficient evidence"* —
   never *"approved"*, *"denied"*, or *"covered"*.
4. **Metadata gaps are visible.** Missing version, effective date, section, or
   page renders as `not available`, never blank and never guessed.
5. **Verification is one click deep.** From any citation, the adjuster reaches the
   exact page and highlighted passage, and can return without losing context.
6. **Decision-support framing is always on screen.** A persistent notice states
   that the system is decision support and does not replace human, legal,
   compliance, or underwriting judgment.

---

## Key UI States

| State | Trigger | Rendering |
|---|---|---|
| `answering` | Question submitted | Loading indicator with stage label |
| `grounded` | Sufficient supporting evidence | Answer + inline citations + evidence list |
| `weak_evidence` | Top score below threshold | Uncertainty response + review warning; **no definitive answer** |
| `conflicting` | Unresolved conflict between authoritative sources | Both positions shown side by side + escalation notice |
| `no_evidence` | No chunk supports the question | Explicit insufficient-evidence response + suggested next step |
| `error` | Retrieval/LLM failure | Error panel with query ID; **no partial answer presented as final** |
| `superseded` | Retrieved version not in effect on date of loss | Version warning + the version that applies |

---

## Acceptance Criteria

| ID | Criterion |
|---|---|
| UX-01 | Answer or explicit insufficient-evidence response renders within P95 ≤ 10 s |
| UX-02 | Every evidence excerpt shows document, section, and page; missing fields render `not available` |
| UX-03 | 100% of citations resolve to a real indexed source |
| UX-04 | ≥ 90% of exclusion, endorsement, conflict, and insufficient-evidence questions display a visible warning |
| UX-05 | Version-conflict questions show either the version in effect on the stated date, or a conflict warning |
| UX-06 | Selecting a citation opens the source at the relevant page with the passage highlighted |
| UX-07 | Knowledge-base status (documents, chunks, last ingest, p95 latency) is visible from the dashboard |
| UX-08 | No screen renders language implying claim approval, denial, or settlement |
