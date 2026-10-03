# Phase 09 — Deployment & Documentation

**LUs:** 3.49–3.50 (Core) · **Status:** ⬜ Blocked on Q-07
**Spec:** [DEPLOYMENT.md](../docs/DEPLOYMENT.md) · FR-20

---

## Scope

Someone else must be able to clone, configure, run, evaluate, and deploy this
without asking you a question.

## Tasks

- [ ] Confirm logging and document-handling constraints (Q-07)
- [ ] Deployment target selected; topology defined
- [ ] Container image; secrets **not** in the image or repo
- [ ] Health check, alerting on p95 latency and error rate
- [ ] Re-run the full evaluation against the **deployed** configuration
- [ ] Documentation complete:
  - [ ] Setup and quick start
  - [ ] Environment variables
  - [ ] Ingestion / indexing
  - [ ] API usage
  - [ ] Evaluation methodology and results
  - [ ] Deployment runbook and troubleshooting
- [ ] Final submission: PRD §16 pre-submission gates
- [ ] Risk and assumption review closed out
- [ ] Alignment record updated with reviewer sign-off status

## Exit Criteria

- [ ] Fresh clone → running system using only the documentation
- [ ] Full evaluation re-run against the deployed configuration, all metrics reported
- [ ] P95 latency ≤ 10 s measured **in the deployed environment**
- [ ] Secrets managed outside the repo and image
- [ ] No claim content or personal data in logs, verified against Q-07
- [ ] `GET /health` wired to a real health check
- [ ] PRD §16 gates addressed; alignment record updated
- [ ] All unverified items still marked TBD — **nothing invented to look complete**

## Blockers

| Blocker | Owner |
|---|---|
| Q-07 — logging / privacy constraints | Technical / compliance reviewer |
