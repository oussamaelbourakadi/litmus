"""Litmus CLI (Typer): init, run (CI gate), report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer

from litmus.compare import compare
from litmus.config import Config, load_config
from litmus.evaluators import build_evaluator
from litmus.models import RunResult
from litmus.runner import Target, http_target, python_target, run_local

app = typer.Typer(help="Litmus — evaluate AI systems from the CLI and gate CI on regressions.")

_LITMUS_YAML = """\
name: demo-qa
target:
  type: python
  entrypoint: demo_target:answer
dataset: datasets/qa.json
evaluators:
  - type: exact_match
repeats: 1
seed: 0
threshold:
  mode: absolute
  max_drop: 0.0
baseline: baseline.json
"""

_DEMO_TARGET = '''\
"""A tiny deterministic target for the Litmus demo (no API key)."""

ANSWERS = {
    "capital of France?": "Paris",
    "2+2?": "4",
    "color of the sky?": "blue",
}


def answer(prompt: str) -> str:
    return ANSWERS.get(prompt.strip(), "I don't know")
'''

_QA_JSON = """\
[
  {"input": "capital of France?", "expected": "Paris"},
  {"input": "2+2?", "expected": "4"},
  {"input": "color of the sky?", "expected": "blue"}
]
"""

_BASELINE_JSON = '{"success_rate": 1.0}\n'


def _build_target(cfg: Config) -> Target:
    target_type = str(cfg.target.get("type", "python"))
    if target_type == "python":
        entrypoint = cfg.target.get("entrypoint")
        if not isinstance(entrypoint, str):
            raise typer.BadParameter("python target requires 'entrypoint'")
        return python_target(entrypoint, search_path=cfg.config_dir)
    if target_type == "http":
        url = cfg.target.get("url")
        if not isinstance(url, str):
            raise typer.BadParameter("http target requires 'url'")
        return http_target(
            url,
            input_field=str(cfg.target.get("input_field", "input")),
            output_field=str(cfg.target.get("output_field", "output")),
        )
    raise typer.BadParameter(f"unknown target type: {target_type!r}")


def _serialize_run(name: str, run: RunResult) -> dict[str, Any]:
    return {
        "name": name,
        "success_rate": run.success_rate,
        "ci_low": run.ci_low,
        "ci_high": run.ci_high,
        "latency_p50": run.latency_p50,
        "latency_p95": run.latency_p95,
        "total": run.total,
        "passed": run.passed,
        "errors": run.errors,
        "cases": [
            {
                "input": r.input,
                "output": r.output,
                "passed": r.passed,
                "latency_ms": r.latency_ms,
                "error": r.error,
            }
            for r in run.results
        ],
    }


@app.command()
def init(
    path: Annotated[Path, typer.Option("--path", "-p", help="Directory to scaffold into")] = Path(
        "."
    ),
) -> None:
    """Scaffold a litmus.yaml, a demo target, a dataset, and a baseline."""
    path.mkdir(parents=True, exist_ok=True)
    (path / "datasets").mkdir(exist_ok=True)
    (path / "litmus.yaml").write_text(_LITMUS_YAML, encoding="utf-8")
    (path / "demo_target.py").write_text(_DEMO_TARGET, encoding="utf-8")
    (path / "datasets" / "qa.json").write_text(_QA_JSON, encoding="utf-8")
    (path / "baseline.json").write_text(_BASELINE_JSON, encoding="utf-8")
    typer.echo(f"Scaffolded Litmus config in {path}/")
    typer.echo("Run: litmus run --config litmus.yaml")


@app.command()
def run(
    config: Annotated[Path, typer.Option("--config", "-c", help="Path to litmus.yaml")],
    update_baseline: Annotated[
        bool, typer.Option("--update-baseline", help="Write the baseline")
    ] = False,
    json_out: Annotated[Path | None, typer.Option("--json", help="Write results JSON here")] = None,
) -> None:
    """Run the evaluation locally and gate on regressions (exit 1 on regression)."""
    cfg = load_config(config)
    if not cfg.cases:
        typer.echo("No test cases found in config.", err=True)
        raise typer.Exit(code=2)

    target = _build_target(cfg)
    evaluators = [build_evaluator(spec) for spec in cfg.evaluators]
    result = run_local(cfg.cases, target, evaluators, repeats=cfg.repeats, seed=cfg.seed)

    typer.echo(f"Litmus run: {cfg.name}")
    typer.echo(
        f"  success rate: {result.success_rate:.2%} "
        f"(95% CI [{result.ci_low:.2%}, {result.ci_high:.2%}])"
    )
    typer.echo(f"  cases: {result.total}  passed: {result.passed}  errors: {result.errors}")
    typer.echo(f"  latency P50/P95: {result.latency_p50:.0f}/{result.latency_p95:.0f} ms")

    if json_out is not None:
        json_out.write_text(
            json.dumps(_serialize_run(cfg.name, result), indent=2), encoding="utf-8"
        )

    if cfg.baseline is None:
        return

    if update_baseline or not cfg.baseline.exists():
        cfg.baseline.write_text(
            json.dumps({"success_rate": result.success_rate}, indent=2), encoding="utf-8"
        )
        typer.echo(f"  baseline written to {cfg.baseline.name}")
        return

    baseline_data = json.loads(cfg.baseline.read_text(encoding="utf-8"))
    base_success = float(baseline_data.get("success_rate", 0.0))
    verdict = compare(base_success, result.success_rate, cfg.threshold)
    typer.echo(f"  gate: {verdict.reason}")
    if not verdict.passed:
        typer.echo("REGRESSION detected — failing the build.", err=True)
        raise typer.Exit(code=1)
    typer.echo("Gate passed.")


@app.command()
def report(
    results: Annotated[
        Path, typer.Option("--results", "-r", help="Results JSON from `run --json`")
    ],
    out: Annotated[Path, typer.Option("--out", "-o", help="Markdown output path")] = Path(
        "report.md"
    ),
) -> None:
    """Render a Markdown report from a results JSON file."""
    data = json.loads(results.read_text(encoding="utf-8"))
    lines = [
        f"# Litmus report — {data.get('name', 'run')}",
        "",
        f"- **Success rate:** {float(data.get('success_rate', 0.0)):.2%} "
        f"(95% CI [{float(data.get('ci_low', 0.0)):.2%}, {float(data.get('ci_high', 0.0)):.2%}])",
        f"- **Cases:** {data.get('total', 0)} · **Passed:** {data.get('passed', 0)} "
        f"· **Errors:** {data.get('errors', 0)}",
        f"- **Latency P50/P95:** {float(data.get('latency_p50', 0.0)):.0f} / "
        f"{float(data.get('latency_p95', 0.0)):.0f} ms",
        "",
        "| Input | Output | Result |",
        "| --- | --- | --- |",
    ]
    for case in data.get("cases", []):
        verdict = "pass" if case.get("passed") else "fail"
        lines.append(f"| {case.get('input', '')} | {case.get('output', '')} | {verdict} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    typer.echo(f"Report written to {out}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
