<div align="center">

# Coverage Intel

**Verify Coverage. Ground Every Decision.**

A RAG-based **insurance coverage intelligence assistant** that helps claims
adjusters find, interpret, and **cite** the policy language that actually applies
to a claim — across hundreds of overlapping policy documents, claim guidelines,
underwriting manuals, and endorsements.

[![Status](https://img.shields.io/badge/status-scaffold%20in%20progress-amber)](#project-status)
[![Sprint](https://img.shields.io/badge/sprint-2%20%C2%B7%20RAG%2FLLM%20track-blue)](#)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776ab?logo=python&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](#license)

</div>

---

> **This is decision support — not claim adjudication.**
> Coverage Intel does **not** approve or deny claims, calculate settlements,
> authorize payment, modify policy terms, or replace required human, legal,
> compliance, or underwriting judgment. Every answer is evidence-grounded and
> traceable to a cited source, and the system refuses to answer when the
> evidence is insufficient or conflicting.

---

## The Problem

An insurance provider holds policy documents, claim guidelines, and underwriting
manuals — but adjusters **misquote coverage terms**, because the answers they need
are buried across hundreds of overlapping, versioned, sometimes conflicting
documents.

Document *search* is not the problem. The problem is **applicability**: knowing
*which* language governs *this* claim, on *this* date, in *this* jurisdiction,
after *this* endorsement, and being able to show your work.

## The Solution

Coverage Intel answers a coverage question by:

1. **Retrieving** candidate policy chunks (semantic + keyword, hybrid, metadata-filtered).
2. **Reranking** them by true relevance.
3. **Checking applicability** — version, effective period, jurisdiction, endorsement relationship, source authority.
4. **Detecting conflicts and exclusions** instead of silently picking one source.
5. **Generating a grounded answer** at temperature ≤ 0.2, constrained to retrieved evidence only.
6. **Citing** the exact document, section, and page behind every claim.
7. **Refusing to answer** when the evidence doesn't support a conclusion.

## Project Status

This repository is currently a **scaffold**. The architecture, specification,
evaluation contract, and phase plan are defined; implementation lands
phase-by-phase against those specs.

| Area | Status |
|---|---|
| PRD & product scope | ✅ Defined ([docs/PRD.md](docs/PRD.md)) |
| UX flows & screens | ✅ Defined ([docs/UX.md](docs/UX.md)) |
| Technical spec & architecture | ✅ Defined ([docs/SPEC.md](docs/SPEC.md)) |
| API contract | ✅ Defined ([docs/API.md](docs/API.md)) |
| Evaluation harness & metrics | ✅ Defined ([docs/EVALUATION.md](docs/EVALUATION.md)) |
| Phase plan & LU traceability | ✅ Defined ([docs/ROADMAP.md](docs/ROADMAP.md)) |
| Approved document corpus | ⏳ **Pending knowledge-owner sign-off** |
| Implementation | ⬜ Not started — see [phases/](phases/) |

---

## Quick Start

```bash
git clone https://github.com/kalviumcommunity/s66_vortex_coverage-intel.git
cd s66_vortex_coverage-intel

cp .env.example .env        # fill in your API keys
make install                # python -m venv + pip install -e ".[dev]"

# 1. Place approved source documents in data/corpus/
# 2. Ingest → embed → index
make ingest
make index

# 3. Ask a coverage question
make ask QUESTION="Is water damage from a burst pipe covered under the HO-3?"

# 4. Run the evaluation suite
make eval
```

Full setup, environment variables, and deployment instructions:
**[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**.

---

## Repository Layout

```
coverage-intel/
├── docs/            Product + technical documentation (PRD, spec, API, eval, deploy)
├── specs/           Numbered build contracts — the source of truth for implementation
├── phases/          Phase-by-phase delivery plan with exit criteria
├── src/coverage_intel/
│   ├── ingestion/     # loading, cleaning, chunking, metadata      (FR-01..FR-05)
│   ├── embeddings/    # encoding + quality checks                  (FR-06)
│   ├── vectorstore/   # indexing, persistence                      (FR-07)
│   ├── retrieval/     # semantic, keyword, hybrid, rerank          (FR-08..FR-10)
│   ├── generation/    # prompts, context, grounding, guardrails    (FR-11..FR-14)
│   ├── pipeline/      # end-to-end RAG orchestration
│   ├── api/           # FastAPI app, routes, auth                   (FR-15..FR-16)
│   └── evaluation/    # metrics + repeatable eval runner           (FR-18)
├── ui/              Coverage assistant / dashboard / evidence viewer
├── evals/           Golden set + labelled coverage questions
├── data/corpus/     Approved source documents (git-ignored)
├── scripts/         CLI entrypoints
└── tests/           Unit + integration tests
```

---

## The Four Product Surfaces

| Surface | Purpose |
|---|---|
| **Coverage Dashboard** | Entry point; knowledge-base health, recent investigations, suggested inquiries |
| **Coverage Assistant** | The core flow — ask a question, get a grounded answer with inline citations and warnings |
| **Policy Search & Evidence Verification** | Open the cited source, jump to section/page, highlight the exact supporting passage |
| **RAG Evaluation & Governance** | Run the benchmark, inspect retrieval traces, verify citations, find discrepancies |

See [docs/UX.md](docs/UX.md) for full flows and acceptance criteria.

---

## How Grounding Is Enforced

This is the heart of the system — the guardrails that make an answer
trustworthy or make it refuse to exist:

| Guardrail | Behaviour |
|---|---|
| **Similarity threshold** | If the top retrieval score falls below the configured threshold → return an *insufficient evidence* response, not an answer. |
| **No-support detection** | If no retrieved chunk supports the question → *insufficient evidence*, never a guess. |
| **Conflict detection** | If two authoritative sources disagree and precedence can't be resolved from metadata → surface the conflict, request human review. Do not silently choose. |
| **Version awareness** | Among versions of the same document, the one in effect **on the date of loss** applies. An out-of-date version must never be presented as governing. |
| **Endorsement precedence** | An endorsement overrides the base policy it is linked to. |
| **Citation requirement** | Every answer statement must carry a citation resolving to a real indexed source. |
| **Low temperature** | Generation runs at temperature ≤ 0.2 to minimise drift from evidence. |
| **Metadata incompleteness** | A chunk missing version/effective-date is flagged and surfaced, not silently trusted. |

---

## Success Metrics

Targets are validated against a labelled evaluation set of **40+ questions**:
20 normal coverage, 8 exclusion/endorsement, 6 version-conflict, 6 insufficient-evidence.

| Metric | Target | Method |
|---|---|---|
| Retrieval relevance | ≥ 85% | Supporting chunk in top-5 |
| Citation correctness | ≥ 90% support, 100% resolve | Citation-to-statement entailment |
| Grounded answer rate | ≥ 90% | Unsupported-claim audit |
| Uncertainty / escalation handling | ≥ 90% | Refusal on weak/conflicting evidence |
| Response latency | ≤ 10 s (P95) | End-to-end, deployed environment |
| Ingestion success | ≥ 95% | Text + required metadata extracted |

No development question used to tune retrieval is reused for final scoring.
Full methodology: [docs/EVALUATION.md](docs/EVALUATION.md).

---

## Contributing

Read [AGENTS.md](AGENTS.md) before making changes — it defines the engineering
contract for this repository, the working conventions, and the rules the
implementation must not break. Contribution workflow: [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).

> Corpus documents are **not** committed to this repository. Only approved,
> redistributable reference material may be added; real policy documents stay in
> the knowledge owner's environment.
