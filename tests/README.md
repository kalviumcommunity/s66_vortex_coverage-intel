# Tests

```bash
pytest              # all
pytest -m integration   # requires live services
make check          # lint + types + tests
```

## Required Coverage

Per [AGENTS.md §6](../AGENTS.md), guardrail logic **must** include a refusal
test. A test suite that only exercises the happy path is not acceptable for
anything in `generation/`.

| Area | Must cover |
|---|---|
| `ingestion` | Per-format extraction; boilerplate removal **and** clause-reference preservation; chunk invariants C-1..C-5; `metadata_incomplete` flagging |
| `retrieval` | Top-K ordering; filter isolation; effective-date resolution; hybrid α sweep |
| `generation` | **All five guardrail triggers, including every refusal path**; I-7 citation enforcement; temperature ≤ 0.2 |
| `api` | Contract tests per endpoint; `401` without access key; `status != grounded` → 200; no adjudication language in any response |
| `evaluation` | Metric maths; dev ∩ golden = ∅ check |

## Non-negotiable assertions

- A superseded version is never cited as applicable
- Precedence never derives from similarity score
- A `GROUNDED` answer always has resolvable citations
- Logs contain no claim content or personal data
- No response implies approval, denial, or settlement
