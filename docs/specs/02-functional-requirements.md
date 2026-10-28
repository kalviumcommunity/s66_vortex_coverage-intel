# 02 — Functional Requirements

Traceability: [PRD §8](../docs/PRD.md#8-functional-requirements).

Each FR maps to a module, a spec, a test, and a verification method. An FR with
no verification method is not implemented — it is merely asserted.

| FR | Requirement (short) | Module | Spec | Verified by |
|---|---|---|---|---|
| **FR-01** | Accept PDF/DOCX/TXT; register unique document ID | `ingestion/loaders.py` | [04](04-ingestion.md) | Loader unit tests; ingestion success ≥ 95% |
| **FR-02** | Extract text preserving document ID, section, page | `ingestion/loaders.py` | [04](04-ingestion.md) | Extraction tests per format |
| **FR-03** | Remove boilerplate; normalise whitespace/encoding without losing meaning | `ingestion/cleaning.py` | [04](04-ingestion.md) | Cleaning tests; clause-reference preservation check |
| **FR-04** | Section-aware, token-aware chunking; 500 tokens / 50 overlap, configurable | `ingestion/chunking.py` | [04](04-ingestion.md) | Chunk size/overlap assertions |
| **FR-05** | Store full metadata; `null` for absent; flag `metadata incomplete` | `ingestion/metadata.py` | [03](03-data-model.md), [04](04-ingestion.md) | 100% `document_id`/`section`/`page` audit |
| **FR-06** | Generate embeddings with the configured model | `embeddings/encoder.py` | [05](05-retrieval.md) | Dimension/shape tests |
| **FR-07** | Store embeddings + metadata in the vector DB | `vectorstore/index.py` | [05](05-retrieval.md) | Index round-trip test |
| **FR-08** | Top-5 retrieval (K configurable) with scores and metadata | `retrieval/semantic.py` | [05](05-retrieval.md) | recall@5 ≥ 85% |
| **FR-09** | Metadata filters + semantic/keyword hybrid | `retrieval/hybrid.py` | [05](05-retrieval.md) | Filter-isolation tests; α sweep |
| **FR-10** | Evaluate retrieval on labelled set; tune configuration | `evaluation/` | [08](08-evaluation.md) | `scripts/evaluate.py --suite golden` |
| **FR-11** | Bounded context within model token limit; preserve source IDs | `generation/context.py` | [06](06-generation-and-guardrails.md) | Context budget tests |
| **FR-12** | Temperature ≤ 0.2; prohibit unsupported claims | `generation/answer.py` | [06](06-generation-and-guardrails.md) | Config assertion + prompt review |
| **FR-13** | Display document + section/page linked to the evidence | `generation/citations.py` | [06](06-generation-and-guardrails.md) | 100% citation resolution |
| **FR-14** | Return uncertainty/review when score < threshold or no support | `generation/guardrails.py` | [06](06-generation-and-guardrails.md) | Refusal test cases (required) |
| **FR-15** | QA + upload endpoints returning answer, citations, warnings | `api/routes.py` | [07](07-api-contract.md) | API contract tests |
| **FR-16** | Access-key-protected runtime ingest/embed/index | `api/routes.py`, `api/security.py` | [07](07-api-contract.md) | `401` without key; retrievable ≤ 5 min |
| **FR-17** | Coverage-question UI with answer, evidence, citations, warnings | `ui/` | [UX](../docs/UX.md) | UX acceptance criteria UX-01..UX-08 |
| **FR-18** | Repeatable evaluation reporting every PRD §5 metric | `evaluation/runner.py` | [08](08-evaluation.md) | Evaluation report contains all 6 metrics |
| **FR-19** | Log query ID, timestamp, chunk IDs, latency, errors; **no claim data** | `logging_config.py` | [06](06-generation-and-guardrails.md) | Log schema test + privacy review |
| **FR-20** | Document setup, env vars, ingestion, retrieval, eval, API, deployment | `docs/` | [DEPLOYMENT](../docs/DEPLOYMENT.md) | Doc checklist in Phase 09 |

---

## Requirement Quality Rules

Per [PRD §14](../docs/PRD.md#14-prd-language--documentation-standards):

| ❌ Never | ✅ Instead |
|---|---|
| "accurate answers" | measured by grounded-answer rate + citation support |
| "fast" | measured by P95 end-to-end latency |
| "appropriate documents" | named source categories + authority validation |
| "user-friendly UI" | enumerated UX acceptance criteria |
| "relevant results" | recall@5 against a labelled set |

---

## Module Boundary Rules

| Module | May import | Must **not** import |
|---|---|---|
| `ingestion` | `config`, domain models | `retrieval`, `generation`, `api` |
| `embeddings` / `vectorstore` | `config`, domain models | `generation`, `api` |
| `retrieval` | `config`, domain models, `vectorstore`, `embeddings` | `generation`, `api` |
| `generation` | `config`, domain models | `api`, `ingestion` |
| `pipeline` | everything below it | — |
| `api` | everything below it | — |

Provider SDKs appear **only** inside the interface implementations in
`embeddings/`, `vectorstore/`, and `generation/llm.py`. They must not leak into
pipeline logic.
