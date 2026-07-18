# Litmus SDK + CLI

Evaluate AI systems locally and gate CI on regressions — no server, no API key.

## Install

```bash
uv pip install ./sdk        # or: pip install ./sdk
```

## CLI

```bash
litmus init                       # scaffold litmus.yaml + a demo target
litmus run --config litmus.yaml   # run locally; exits non-zero on regression
litmus run --config litmus.yaml --json results.json
litmus report --results results.json --out report.md
```

`litmus run` runs the target over the dataset, computes the success rate (with a
seeded bootstrap CI), and compares it to a committed `baseline.json`. If the
success rate drops beyond the configured threshold, it exits with code 1 — which
fails the CI build.

## SDK (run in ~10 lines)

```python
from litmus import Case, ExactMatch, run_local

cases = [Case(input="capital of France?", expected="Paris")]

def target(prompt: str) -> str:
    return "Paris"

result = run_local(cases, target, [ExactMatch()])
print(result.success_rate, result.ci_low, result.ci_high)
```
