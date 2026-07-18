"""Litmus SDK quickstart — a local evaluation run in ~10 lines."""

from litmus import Case, ExactMatch, RegexMatch, run_local

cases = [
    Case(input="capital of France?", expected="Paris"),
    Case(input="2+2?", expected="4"),
]


def target(prompt: str) -> str:
    return {"capital of France?": "Paris", "2+2?": "4"}.get(prompt, "?")


result = run_local(cases, target, [ExactMatch(), RegexMatch(r".+")])
print(f"success rate: {result.success_rate:.0%}  CI [{result.ci_low:.0%}, {result.ci_high:.0%}]")
