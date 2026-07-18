"""Local runner tests."""

from __future__ import annotations

from pathlib import Path

from litmus.evaluators import ExactMatch, RegexMatch
from litmus.models import Case
from litmus.runner import python_target, run_local


def test_run_local_all_pass() -> None:
    result = run_local([Case(input="q", expected="a")], lambda _: "a", [ExactMatch()])
    assert result.total == 1
    assert result.passed == 1
    assert result.success_rate == 1.0


def test_run_local_isolates_errors() -> None:
    def boom(_: str) -> str:
        raise RuntimeError("boom")

    result = run_local([Case(input="a"), Case(input="b")], boom, [ExactMatch()])
    assert result.errors == 2
    assert result.success_rate == 0.0
    assert result.results[0].error is not None


def test_and_verdict_requires_all() -> None:
    result = run_local(
        [Case(input="q", expected="a")],
        lambda _: "a",
        [ExactMatch(), RegexMatch(r"\d+")],
    )
    assert result.results[0].passed is False


def test_repeats_multiply_results() -> None:
    result = run_local([Case(input="q", expected="a")], lambda _: "a", [ExactMatch()], repeats=3)
    assert len(result.results) == 3


def test_python_target_loads_callable(tmp_path: Path) -> None:
    (tmp_path / "mytgt.py").write_text("def go(p):\n    return p.upper()\n", encoding="utf-8")
    target = python_target("mytgt:go", search_path=tmp_path)
    assert target("hi") == "HI"
