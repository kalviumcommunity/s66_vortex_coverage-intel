# 04 — Ingestion & Chunking Contract

Traceability: FR-01..FR-05 · [PRD §4](../docs/PRD.md#4-knowledge-source-documentation) · LU 3.19–3.24

---

## Pipeline

```
load ──▶ extract ──▶ clean ──▶ chunk ──▶ attach metadata ──▶ validate ──▶ emit Chunk[]
```

Every stage is **pure and independently testable**. A stage never performs I/O
outside its own boundary.

---

## FR-01 — Document Loading

**Accept:** PDF, DOCX, TXT only. Each source document gets a unique
`document_id`.

```python
def load(path: Path) -> SourceDocument: ...
```

| Rule | Behaviour |
|---|---|
| Unsupported extension | `UnsupportedDocumentType` → HTTP `415` |
| `document_id` derivation | `slug(filename)` + short `checksum` prefix — stable across re-ingest of identical content |
| Duplicate content, new filename | Distinct `document_id` (same policy, different file) |
| Empty file | `CorpusValidationError` — never index an empty document |

---

## FR-02 — Text Extraction

**Accept:** text extracted with `document_id`, `section`, and `page` preserved.

```python
def extract(doc: SourceDocument) -> ExtractedDocument: ...
```

`ExtractedDocument` carries a list of **blocks** (`text`, `section`, `page`,
`char_start`, `char_end`) rather than one flat string — this is what makes
section- and page-aware chunking possible.

| Format | Requirement |
|---|---|
| PDF | Per-page extraction with page numbers preserved |
| DOCX | Heading-style paragraphs mapped to section labels |
| TXT | Line-based; section inferred from heading patterns |

> ⚠️ **Scanned/image PDFs produce empty or garbage text.** This is a known
> limitation ([PRD §10](../docs/ROADMAP.md#blockers--external-dependencies));
> OCR is **out of MVP scope**. Extraction must **fail loudly**, not index noise.

---

## FR-03 — Cleaning

**Accept:** boilerplate removed, whitespace/encoding normalised, **meaning
preserved**.

```python
def clean(blocks: list[Block]) -> list[Block]: ...
```

### Removed

| Pattern | Detection |
|---|---|
| Page headers / footers | Line appearing on ≥ 60% of pages with low lexical variance |
| Standalone page numbers | Regex `^\s*(page\s+)?\d+(\s+of\s+\d+)?\s*$`, case-insensitive |
| Watermarks / "DRAFT" marks | Repeated-token detection across pages |
| Bullet glyph noise | Normalised, not deleted |
| Excess whitespace | Collapsed runs → single space; paragraph breaks preserved |

### Preserved — deleting these is a bug

- Numbered clause references — `Section 7.2`, `§ 4(b)(3)`, `(i)`
- Defined terms — `"Loss" means …`
- Sentence structure and negation
- Currency amounts, percentages, limits
- Headings that carry no body text (e.g. a standalone exclusion title)

---

## FR-04 — Chunking

**Accept:** section-aware **and** token-aware. Defaults **500 tokens**,
**50-token overlap**, both configurable.

```python
def chunk(blocks: list[Block], size: int = 500, overlap: int = 50) -> list[Chunk]: ...
```

### Algorithm

1. **Group** blocks by `section`.
2. If no headings were detected, use a single synthetic section —
   **never** discard the hierarchy silently.
3. **Within** each section, accumulate tokenised sentences up to `size`.
4. On overflow, emit a chunk and start the next with a trailing
   `overlap`-token tail.
5. **Do not merge across a section boundary** — except when a whole section is
   smaller than `size`, in which case merge forward and record **both** section
   labels.
6. A chunk spanning pages sets `page` = first page, `page_end` = last page.

### Invariants

| # | Invariant |
|---|---|
| C-1 | `chunk.token_count <= size` |
| C-2 | Consecutive chunks in the same section share `overlap` tokens |
| C-3 | Every chunk has a non-empty `text` |
| C-4 | `chunk_id` is unique across the corpus |
| C-5 | `char_start < char_end` when either is present |

`overlap < size` is validated at construction; the config loader rejects
otherwise.

---

## FR-05 — Metadata

**Accept:** document, policy, version, effective-date, jurisdiction, section,
page, endorsement, chunk ID stored for every chunk. Absent fields are `null`
and the chunk is flagged `metadata incomplete`.

```python
def attach(chunk: Chunk, doc: SourceDocument, corpus_manifest: Manifest) -> Chunk: ...
```

| Field | Source |
|---|---|
| `category`, `version`, `effective_from/to`, `jurisdiction`, `linked_policy_id` | `SourceDocument` or corpus manifest |
| `section`, `page`, `char_start/end` | Extraction |
| `chunk_id`, `token_count` | Chunking |
| `metadata_incomplete`, `missing_fields` | Computed |

```python
REQUIRED_TRACEABILITY = ["document_id", "section", "page"]
VERSION_FIELDS        = ["version", "effective_from"]
```

### Rules

- Missing `version` / `effective_from` ⇒ `metadata_incomplete=True` and
  `missing_fields` names them.
- **A chunk is never dropped for missing metadata** — it is flagged and the gap
  is surfaced downstream as `METADATA_INCOMPLETE` (FR-14).
- Absent values are `None`, never `""`, `"N/A"`, or `"unknown"`.

---

## Corpus Validation

Prevents unapproved or unusable documents entering the index (PRD §4.1).

| Check | Failure |
|---|---|
| File type supported | `UnsupportedDocumentType` |
| Non-empty extracted text | `CorpusValidationError` — likely a scan |
| `document_id` resolvable | `CorpusValidationError` |
| Endorsement has `linked_policy_id` | `CorpusValidationError` |
| Source authority declared | **Warning** — unapproved source is not authoritative evidence |
| `effective_from <= effective_to` | `CorpusValidationError` |

Validation emits a **report** (`scripts/ingest.py --validate`):

```
corpus: 214 documents
  indexed                 : 212 (99.1%)   target ≥ 95%  ✅
  failed validation       : 1   (SCAN_NO_TEXT: scanned PDF)
  metadata_incomplete     : 2
    UW-MAN-2023.pdf        missing: effective_from
    CG-HO-CLAIMS.docx      missing: version
  unapproved authority    : 0
```

---

## Exit Criteria (LU 3.19–3.24)

- [ ] PDF, DOCX, TXT loaders with per-format tests
- [ ] Section and page preserved through extraction
- [ ] Cleaner removes boilerplate and preserves clause references (test both)
- [ ] Chunker satisfies C-1..C-5 at default and non-default config
- [ ] Every chunk carries `document_id`, `section`, `page`
- [ ] Missing version/effective date ⇒ `metadata_incomplete`, chunk not dropped
- [ ] Ingestion success ≥ 95% on the test corpus
- [ ] Corpus validation report generated
- [ ] Scanned documents fail loudly rather than indexing noise
