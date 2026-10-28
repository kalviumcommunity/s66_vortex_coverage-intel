# Coverage Intel — Application Summary & Guidelines

This document combines and supersedes **`AGENTS.md`** and **`CONTRIBUTING.md`**. It serves as the authoritative engineering contract and development workflow guide for human contributors and automated coding agents working on **Coverage Intel**.

---

## 1. Project Purpose & Scope

Coverage Intel is a **retrieval-augmented generation (RAG)** decision-support assistant that answers insurance coverage questions for claims adjusters, grounded strictly in approved policy documents and authoritative references.

> **Decision Support Boundary**: This application is strictly decision support. No code path may approve, deny, settle, authorize payment, calculate settlements, or replace human, legal, compliance, or underwriting judgment.

---

## 2. Non-Negotiable Product Rules

These are binding invariants. Breaking any of these rules invalidates the system:

1. **No Unsupported Claims**: Every coverage statement in a generated answer must be grounded in a retrieved chunk that is cited inline. When evidence is insufficient, the system must return an explicit `insufficient_evidence` response.
2. **Never Fabricate Citations**: A citation must resolve to an authentic chunk in the index (`document_id`, `section`, `page`). Missing fields must be rendered as `not available` and never hallucinated.
3. **Never Silently Resolve Conflicts**: When two authoritative sources conflict and precedence cannot be resolved by validated metadata, the system surfaces the contradiction and flags human review.
4. **Mandatory Version Awareness**: An outdated document must never govern if effective dates are present. The policy in effect on the **date of loss** governs.
5. **Endorsement Precedence**: An endorsement always takes precedence over the base policy form it modifies.
6. **No Invented Facts**: Do not fabricate metrics, corpus counts, stakeholder names, or validation statuses. Unverified items remain marked `TBD` or `pending validation`.
7. **Privacy & Security in Logs**: Log query IDs, latency, chunk IDs, and error codes. Never log full claim narratives, policyholder identifiers, or personal information.

---

## 3. Implementation Conventions

- **Python 3.11+**, typed, strict `src/` layout under package `coverage_intel`.
- **Pydantic v2**: Every boundary type (configuration, chunk metadata, retrieval payloads, API schemas) is a typed Pydantic model. Metadata must never be handled as an untyped dictionary.
- **Immutable Domain Types**: Retrieved chunks, evidence sets, and citations are treated as immutable once indexed.
- **Chunk Metadata Schema**: Every chunk must carry `document_id`, `section`, `page`, and a stable `chunk_id`. `version` and `effective_date` are recorded when present; otherwise the chunk is flagged with `metadata_incomplete=True`.
- **Environment-Driven Configuration**: All secrets, model endpoints, vector store configurations, and retrieval thresholds live in `src/coverage_intel/config.py` and are populated via `.env` (prefixed with `CI_`, `PINECONE_`, or `XAI_GROK_`). Never hardcode credentials or model parameters.
- **Versioned Prompts**: Prompts are stored as templates in `generation/prompts.py`, never inline strings scattered in service logic.
- **Structured JSON Output**: Model answers are emitted adhering to strict JSON schemas; never parse raw unstructured prose using regex.
- **Typed Error Hierarchy**: LLM timeouts, retrieval failures, and guardrail refusals use explicit, typed exception classes.

---

## 4. RAG Pipeline Architecture

```
Ingestion  →  Embeddings  →  Vector Store (Pinecone / In-Memory)
                                   ↓
User Query  ───────────────→  Retrieval (Hybrid Dense + BM25 + Metadata Filters)
                                   ↓
                              Applicability & Conflict Analysis
                                   ↓
                              Context Assembly (Token-bounded, chunk IDs preserved)
                                   ↓
                              Grounded Generation (Temperature ≤ 0.2)
                                   ↓
                              Citation Validation & Guardrails
                                   ↓
                              REST API / Modern Web UI + Structured Telemetry
```

Pipeline stage order is fixed. Bypassing any stage requires explicit configuration and must be surfaced in the response payload.

---

## 5. Development Workflow

1. **Issues & Branching**: Branch from `main` using descriptive prefixes (`feat/<slug>`, `fix/<slug>`, `docs/<slug>`, `eval/<slug>`).
2. **Spec First**: Review the specifications under `docs/specs/` before implementing new features.
3. **One Concern Per Change**: Avoid bundling ingestion refactors with generation or frontend modifications.
4. **Test Everything**: Any new retrieval or guardrail feature must include unit tests verifying both the happy path and the refusal path.
5. **Validation Suite**: Run `pytest` before opening PRs. All tests must pass.
6. **Commit Message Format**:
   ```
   <type>: <imperative summary>
   
   Refs: US-04, FR-05
   Spec: docs/specs/04-ingestion.md
   ```
   *Allowed types*: `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `chore`, `eval`.

---

## 6. Evaluation & Golden Set Discipline

- The golden benchmark set (`evals/golden/golden_set.example.jsonl`) is held out. Never tune retrieval on individual evaluation questions.
- If a change modifies chunk size, overlap, embedding models, vector store indexing, similarity thresholds, hybrid alpha, or generation prompts, re-run the evaluation suite and record metrics across all categories.
- Always monitor retrieval relevance, citation correctness, grounded-answer rate, uncertainty handling, and P95 latency. A change that increases speed while reducing citation precision is unacceptable.

---

## 7. Sensitive Data Restrictions

Never commit `.env`, live API credentials (`PINECONE_API_KEY`, `XAI_GROK_API_KEY`), real insurance claim files, or evaluation traces containing customer data. All active policies and corpus files reside in `data/corpus/` and are excluded via `.gitignore`.

