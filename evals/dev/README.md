# Dev Set — Tuning

**Free to tune retrieval against.** Questions here may be used to select chunk
size, overlap, α, top-K, filters, and reranking.

They must **never** appear in `evals/golden/`. The harness fails the run if a
golden `qid` also appears here.

Same schema as [`../golden/schema.json`](../golden/schema.json).

```bash
make eval-retrieval
```
