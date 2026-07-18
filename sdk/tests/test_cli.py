"""CLI tests via Typer's CliRunner (exit codes matter for the CI gate)."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from litmus.cli import app

runner = CliRunner()


def _scaffold(tmp_path: Path) -> Path:
    result = runner.invoke(app, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0
    return tmp_path / "litmus.yaml"


def test_init_then_run_passes(tmp_path: Path) -> None:
    config = _scaffold(tmp_path)
    result = runner.invoke(app, ["run", "--config", str(config)])
    assert result.exit_code == 0
    assert "Gate passed" in result.stdout


def test_run_exits_nonzero_on_regression(tmp_path: Path) -> None:
    config = _scaffold(tmp_path)
    # Sabotage the target so the success rate drops below the baseline.
    (tmp_path / "demo_target.py").write_text(
        "def answer(p):\n    return 'wrong'\n", encoding="utf-8"
    )
    result = runner.invoke(app, ["run", "--config", str(config)])
    assert result.exit_code == 1


def test_report_generates_markdown(tmp_path: Path) -> None:
    config = _scaffold(tmp_path)
    results_json = tmp_path / "results.json"
    runner.invoke(app, ["run", "--config", str(config), "--json", str(results_json)])

    out = tmp_path / "report.md"
    result = runner.invoke(app, ["report", "--results", str(results_json), "--out", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "Litmus report" in out.read_text(encoding="utf-8")
