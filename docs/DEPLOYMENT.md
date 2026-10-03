# Setup & Deployment — Coverage Intel

> Implements FR-20. Covers local development, environment configuration, and
> deployment. Key names use the `CI_` prefix from `src/coverage_intel/config.py`.

---

## 1. Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| `uv` *or* `pip` + `venv` | latest |
| Docker | optional — for Qdrant in production |
| LLM provider account | with API access and quota |
| Embedding provider account | with API access and quota |

---

## 2. Local Setup

```bash
git clone https://github.com/sangeeth-606/coverage-intel.git
cd coverage-intel

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
$EDITOR .env          # fill in CI_LLM_API_KEY, CI_EMBEDDING_API_KEY, CI_UPLOAD_ACCESS_KEY
```

### Make targets

```bash
make install     # editable install with dev extras
make ingest       # parse, clean, chunk data/corpus/
make index        # embed and index chunks
make ask QUESTION="..." [DATE_OF_LOSS=2025-03-14]
make eval         # run the golden evaluation suite
make api          # serve the API with reload
make ui           # launch the frontend
make check        # lint + type-check + test
```

---

## 3. Environment Variables

### Required

| Variable | Purpose |
|---|---|
| `CI_LLM_API_KEY` | Generation model credential |
| `CI_EMBEDDING_API_KEY` | Embedding model credential |
| `CI_UPLOAD_ACCESS_KEY` | Protects the upload endpoint (FR-16) — **generate a strong random value** |

### Models

| Variable | Default | Purpose |
|---|---|---|
| `CI_LLM_MODEL` | — | Generation model (FR-12) |
| `CI_EMBEDDING_MODEL` | — | Embedding model (FR-06) |
| `CI_LLM_BASE_URL` | — | Provider base URL |
| `CI_EMBEDDING_BASE_URL` | — | Provider base URL |
| `CI_RERANK_MODEL` | — | Cross-encoder reranker (LU 3.35) |

> **Re-run evaluation after any model change.** Similarity scores are
> model-dependent, so `CI_SIMILARITY_THRESHOLD` must be recalibrated
> ([EVALUATION.md §5](EVALUATION.md#5-thresholds-are-calibrated-not-guessed)).

### Retrieval

| Variable | Default | Purpose |
|---|---|---|
| `CI_TOP_K` | `5` | FR-08 |
| `CI_HYBRID_ALPHA` | `0.7` | Dense weight in hybrid scoring |
| `CI_SIMILARITY_THRESHOLD` | `0.35` | FR-14 refusal threshold — **calibrate, don't inherit** |
| `CI_RELEVANCE_FLOOR` | `0.30` | FR-14 |
| `CI_RERANK_ENABLED` | `false` | LU 3.35 |
| `CI_RERANK_TOP_N` | `20` | Rerank candidate count |

### Ingestion

| Variable | Default | Purpose |
|---|---|---|
| `CI_CHUNK_SIZE_TOKENS` | `500` | FR-04 |
| `CI_CHUNK_OVERLAP_TOKENS` | `50` | FR-04 |
| `CI_CORPUS_DIR` | `data/corpus` | Approved documents |

### Generation

| Variable | Default | Purpose |
|---|---|---|
| `CI_GENERATION_TEMPERATURE` | `0.2` | FR-12 — **do not raise above 0.2** |
| `CI_MAX_CONTEXT_TOKENS` | `6000` | FR-11 |

### Storage & Ops

| Variable | Default | Purpose |
|---|---|---|
| `CI_VECTOR_STORE` | `chroma` | `chroma` \| `qdrant` |
| `CI_QDRANT_URL` | — | Qdrant connection |
| `CI_LOG_LEVEL` | `INFO` | FR-19 |
| `CI_LOG_FORMAT` | `json` | Structured logging |

---

## 4. Running the Pipeline

### Ingest

```bash
make ingest
# or
python scripts/ingest.py --input data/corpus --out data/chunks.jsonl
```

Reads PDF / DOCX / TXT, extracts text with section and page markers, cleans
boilerplate, chunks (500/50, configurable), and attaches metadata. Chunks with
missing version or effective date are flagged `metadata_incomplete` — **not**
dropped (FR-05).

```
ingestion success = 214 files → 212 with text+metadata (99.1%)
flagged metadata_incomplete: 2
  - UW-MAN-2023.pdf  → missing: effective_from
  - CG-HO-CLAIMS.docx → missing: version
```

### Index

```bash
make index
# or
python scripts/index.py --chunks data/chunks.jsonl
```

### Query

```bash
make ask QUESTION="Is water damage from a burst pipe covered?" DATE_OF_LOSS=2025-03-14
```

### Evaluate

```bash
make eval
# or
python scripts/evaluate.py --suite golden --compare-to evals/baselines/baseline.json
```

---

## 5. API

```bash
make api          # http://127.0.0.1:8000
```

| URL | Purpose |
|---|---|
| `/api/v1/ask` | Coverage question |
| `/api/v1/documents` | Knowledge-base listing |
| `/api/v1/documents/upload` | Approved document upload (**`X-Access-Key`**) |
| `/api/v1/chunks/{chunk_id}` | Evidence verification |
| `/api/v1/health` | Health check |
| `/api/v1/metrics` | Prometheus metrics |
| `/docs` | OpenAPI UI |

Full contract: [API.md](API.md).

---

## 6. Production Deployment

### Recommended topology

```
        ┌──────────────┐
        │  Reverse     │  TLS, rate limiting, request size caps
        │  proxy       │
        └──────┬───────┘
               │
     ┌─────────┴──────────┐
     │  FastAPI (N reps)   │  stateless
     └─────────┬──────────┘
               │
   ┌───────────┼────────────┐
   ▼           ▼            ▼
┌────────┐ ┌─────────┐ ┌──────────┐
│ Qdrant │ │ LLM API │ │ Knowledge│
│        │ │ + Embed │ │  base    │
└────────┘ └─────────┘ │ (uploaded│
                       │  docs)   │
                       └──────────┘
```

The API is **stateless**. The vector store and uploaded documents are the only
state. Session/conversation state for LU 3.42, if enabled, needs a store — that
is a known consequence of adding conversational RAG.

### Checklist

- [ ] Secrets in a secret manager, never `.env` in the image or repo
- [ ] `CI_UPLOAD_ACCESS_KEY` rotated and stored securely
- [ ] TLS terminated at the proxy
- [ ] `/documents/upload` additionally restricted by network policy — the access
      key is the only application-level control in MVP
- [ ] Log sink configured; **confirm no claim content is captured** (FR-19)
- [ ] Rate limits aligned with provider quotas
- [ ] Vector DB backed up or rebuilt from source documents
- [ ] Health check wired to `/api/v1/health`
- [ ] Alerting on `p95_latency_ms` (SLO: ≤ 10 s) and error rate
- [ ] Evaluation re-run against the deployed configuration before sign-off

### What is deliberately NOT deployed

The product is **not** exposed for claim approval, denial, settlement
calculation, or policy modification. Any deployment that would allow those
actions is out of scope and must not be built.

---

## 7. Operational Limits

| Limit | Value | Behaviour |
|---|---|---|
| Supported file types | PDF, DOCX, TXT | Others → `415` |
| Scanned PDFs | **Not supported** | OCR is out of MVP scope; validate extraction quality early (PRD §10) |
| Upload size | configurable | `413` when exceeded |
| Context size | `CI_MAX_CONTEXT_TOKENS` | Evidence truncated; recorded in `stages` |
| Provider rate limits | provider-specific | Batch embedding and retries where needed (LU 3.28, optional) |

---

## 8. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `401` on upload | Missing/incorrect `X-Access-Key` | Check `CI_UPLOAD_ACCESS_KEY` is set and the header matches |
| All answers refuse | Threshold too high **or** extraction failed | Inspect `semantic_score` in the response; verify chunks contain real text |
| Good recall, weak answers | Chunk boundaries split policy language | Raise chunk size / overlap, or add section-aware splitting |
| Wrong version cited | `date_of_loss` not supplied | Pass `scenario.date_of_loss` — version resolution depends on it |
| Citations not resolving | Index drift after re-ingest | Re-run `make index`; check `GET /health` chunk count |
| High p95 | Context too large, or no caching | Lower `CI_MAX_CONTEXT_TOKENS` / `CI_TOP_K`; enable caching (LU 3.48) |
| Empty extraction | Scanned PDF | OCR required — **out of MVP scope**, raise with the knowledge owner |

---

## 9. Security & Privacy

- No claim details or personal data in logs (FR-19, PRD §10).
- Uploaded policy documents stay in the deployment's own storage; they are
  **never committed to the repository**.
- The MVP assumes network-level access control for the adjuster-facing surface.
  SSO/RBAC is out of MVP scope and pending the security reviewer's input.
- `.env`, `data/corpus/`, `evals/reports/` are git-ignored.

---

## 10. Documentation Map

| Document | Covers |
|---|---|
| [PRD.md](PRD.md) | Product scope, FRs, metrics |
| [UX.md](UX.md) | Screens, flows, states |
| [SPEC.md](SPEC.md) | Architecture, domain types, algorithms, config |
| [API.md](API.md) | Endpoint contracts |
| [EVALUATION.md](EVALUATION.md) | Metrics, golden set, harness |
| [ROADMAP.md](ROADMAP.md) | Phases, LU traceability, DoD |
| [../AGENTS.md](../AGENTS.md) | Engineering contract |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Contribution workflow |
