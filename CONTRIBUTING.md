# Contributing to Coverage Intel

Read [`AGENTS.md`](AGENTS.md) first — it is the binding engineering contract.
This file covers workflow only.

---

## Workflow

1. **Open an issue** describing the problem, not just the solution.
2. **Branch** from `main`: `feat/<short-slug>`, `fix/`, `docs/`, `chore/`.
3. **Spec first.** New behaviour starts in [`specs/`](specs/). Update the
   matching spec in the same change as the code.
4. **Implement** one concern per change.
5. **Test** it — including the refusal path for anything guardrail-related.
6. **`make check`** — lint, types, tests. All must pass.
7. **Open a PR** linking the issue and the spec it implements.

## Commit messages

```
<type>: <imperative summary>

Refs: US-04, FR-05
Spec: specs/04-ingestion.md
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `chore`, `eval`.

## Pull request checklist

- [ ] Specs updated in the same change
- [ ] Tests added — including the failure/refusal path
- [ ] `make check` passes
- [ ] No new `Any` in domain models
- [ ] No provider SDK imported outside its interface implementation
- [ ] No claim content, personal data, or API keys added
- [ ] Any metric-affecting change re-run against the evaluation suite
- [ ] Any **new** judgement call is recorded as an ADR under `docs/adr/`

## Non-negotiables

These are not review preferences — CI and review will block on them:

1. No unsupported coverage claims without citations
2. No fabricated citations
3. No silently resolved conflicts
4. No version-inapplicable document presented as applicable
5. No adjudication language anywhere
6. No invented metrics, baselines, or approval statuses
7. No claim or personal data in logs

## Evaluation discipline

The **golden set is held out**. Never tune retrieval on it, never reuse a tuning
question for final scoring, and never report a metric without `n`.

If a change affects chunking, embeddings, top-K, filters, thresholds, reranking,
the generation model, temperature, prompts, or the corpus — re-run the full
suite and report every metric, including the ones that went down.

## Committing data

Never commit `.env`, API keys, real policy documents, or evaluation outputs
containing claim details. The corpus lives in `data/corpus/` and is git-ignored.
