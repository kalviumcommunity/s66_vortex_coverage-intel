# Phase 01 — LLM Access & Prompting

**LUs:** 3.12–3.13, 3.17–3.18 (Core) · **Status:** ⬜ Blocked on Q-04
**Spec:** [06](../specs/06-generation-and-guardrails.md)

---

## Scope

Provider access, client abstraction, roles, structured output, and reusable
prompt templates. Retrieval is not part of this phase.

## Tasks

- [ ] Confirm provider, credentials, rate limits, and allowed usage (Q-04)
- [ ] `generation/llm.py` — `LLMClient` protocol + provider implementation
- [ ] Retry and timeout handling; typed `GenerationError`
- [ ] Structured JSON output validated against a Pydantic schema
- [ ] Prompt roles: system / context / user
- [ ] `generation/prompts.py` — versioned templates:
  - [ ] Grounded coverage answer
  - [ ] Insufficient-evidence response
  - [ ] Conflict presentation
- [ ] Decision-support framing baked into the system prompt
- [ ] Config: `CI_LLM_MODEL`, `CI_LLM_BASE_URL`, `CI_LLM_API_KEY`
- [ ] Tests: schema validation, refusal path, token/latency budget

## Exit Criteria

- [ ] Client reachable; model and limits recorded in the README
- [ ] Structured output parses reliably; unparseable output → typed error
- [ ] Prompt templates versioned in `prompts.py`, none inline
- [ ] System prompt prohibits adjudication, unsupported claims, and invented citations
- [ ] Temperature defaults to ≤ 0.2
- [ ] A refusal prompt produces an explicit uncertainty response
- [ ] Tests cover the refusal path, not just the happy path

## Blockers

| Blocker | Owner |
|---|---|
| Q-04 — LLM credentials, quota, usage policy | Technical owner |
