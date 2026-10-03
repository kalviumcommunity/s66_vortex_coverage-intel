# Baselines

Recorded run configurations and metric results.

A baseline is committed after every accepted evaluation run so regressions are
visible by comparison:

```bash
python scripts/evaluate.py --suite golden --compare-to evals/baselines/baseline.json
```

A baseline records the **full run config** — model names, chunk size/overlap,
top-K, α, thresholds, rerank state, and corpus checksum. Without those, a score
is not reproducible and the comparison is meaningless.

> A change that improves one metric while degrading another is **not a pass**.
> Both numbers are reported together, always.
