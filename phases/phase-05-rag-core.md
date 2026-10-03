# Phase 05 — RAG Core, Grounding & Guardrails

**LUs:** 3.37–3.41 (Core) · **Status:** ⬜ Blocked on D-02
**Spec:** [06](../specs/06-generation-and-guardrails.md)

---

## Scope

**The phase that decides whether this product is trustworthy.** Everything else
is plumbing; this is where a wrong answer can be prevented.

## Tasks

- [ ] `pipeline/rag.py` — end-to-end orchestration
- [ ] Stage 8 — applicability & conflict analysis:
  - [ ] Endorsement supersession
  - [ ] Version / effective-period resolution
  - [ ] Jurisdiction preference
  - [ ] Conflict detection
  - [ ] Exclusion detection
- [ ] Stage 9 — `generation/context.py`, bounded context, source IDs preserved
- [ ] Stage 10 — `generation/answer.py`, temperature ≤ 0.2, structured output
- [ ] Stage 11 — `generation/citations.py`, verbatim excerpts, I-7 validator
- [ ] FR-14 — `generation/guardrails.py`, all five triggers, evaluated **before**
      generation
- [ ] Threshold calibration procedure (D-04)
- [ ] `logging_config.py` — FR-19 structured logging, no claim content
- [ ] Tests: every guardrail trigger **including the refusal path**; a test
      asserting similarity never decides precedence

## Exit Criteria

- [ ] Applicability handles endorsement, version, jurisdiction, conflict, exclusion
- [ ] Precedence derives from metadata only — asserted by test
- [ ] Context respects the budget and records truncation
- [ ] Every `GROUNDED` statement carries a resolvable citation
- [ ] All five guardrail triggers tested, including refusals
- [ ] Refusals return 200 with evidence attached
- [ ] Threshold calibrated on the dev set, procedure documented
- [ ] Log audit confirms no claim content or personal data
- [ ] The pipeline **cannot** emit a confident answer without evidence

## Blockers

| Blocker | Owner |
|---|---|
| D-02 — precedence rule (**highest-risk item**) | Knowledge / UW / compliance |
