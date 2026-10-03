# Data

## `corpus/` — Approved Source Documents

**Git-ignored.** Real policy documents are proprietary and are never committed.

Place approved documents here for ingestion. Supported types: **PDF, DOCX, TXT**
(FR-01). Anything else is rejected.

```
data/corpus/
├── policies/           # policy documents
├── claim-guidelines/   # claims-handling guidance
├── underwriting/       # underwriting manuals
└── endorsements/       # endorsements and amendments
```

## Knowledge Validation Gate (PRD §4.1)

Before a document enters the index:

- [ ] Source ownership and access permissions confirmed
- [ ] File type supported and text extraction verified
- [ ] Policy / version / effective-date metadata confirmed where available
- [ ] Source authority and precedence confirmed where documents overlap
- [ ] Document and chunk-level source identifiers recorded
- [ ] Not an unapproved or unknown source

## Generated Artifacts

| Path | Contents | Committed? |
|---|---|---|
| `data/chunks.jsonl` | Chunked corpus with metadata | ❌ |
| `data/index/` | Vector index | ❌ |

Rebuild both with `make ingest && make index`.

> ⚠️ **Scanned / image PDFs produce no usable text.** OCR is **out of MVP scope**.
> Such files fail loudly during validation rather than indexing noise — raise
> with the knowledge owner if the real corpus contains scans.
