# Frontend — Coverage Intel

Four surfaces, specified in [docs/UX.md](../docs/UX.md). Phase 08.

| Surface | Purpose |
|---|---|
| **Coverage Dashboard** | Question entry, KB health, recent investigations |
| **Coverage Assistant** | The core flow — grounded answer, citations, warnings |
| **Evidence Verification** | Open the cited source at the page, passage highlighted |
| **Evaluation & Governance** | Metrics, golden cases, retrieval traces |

## Status

⬜ **Not started.** Stack decision pending (Phase 08).

## Non-negotiable UI rules

These come from [AGENTS.md §2](../AGENTS.md) and are testable:

1. **Citation display is core**, not optional — even if streaming is skipped.
2. **Warnings are first-class components**, never footnotes or toasts.
3. **Missing metadata renders `not available`** — never blank, never guessed.
4. **No screen renders approval, denial, coverage, or settlement language.**
   Use evidence language: *"evidence supports"*, *"evidence conflicts"*,
   *"insufficient evidence"*.
5. **A decision-support notice is always visible** on the assistant surface.
6. **Citations resolve in one click**, and the adjuster can return without
   losing the investigation context.

## Required States

`answering` · `grounded` · `weak_evidence` · `conflicting` · `no_evidence` ·
`error` · `superseded`

Each has a defined rendering in [docs/UX.md](../docs/UX.md#key-ui-states).
