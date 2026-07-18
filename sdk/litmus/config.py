"""Load and validate a ``litmus.yaml`` config.

Dataset and baseline paths are resolved relative to the config file's directory.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from litmus.models import Case, Threshold


@dataclass(slots=True)
class Config:
    name: str
    target: dict[str, Any]
    cases: list[Case]
    evaluators: list[dict[str, Any]]
    repeats: int
    seed: int
    threshold: Threshold
    config_dir: Path
    baseline: Path | None = None
    extra: dict[str, Any] = field(default_factory=dict)


def _load_cases(data: dict[str, Any], config_dir: Path) -> list[Case]:
    if "dataset" in data:
        dataset_path = config_dir / str(data["dataset"])
        raw = json.loads(dataset_path.read_text(encoding="utf-8"))
        rows = raw if isinstance(raw, list) else []
    elif "cases" in data and isinstance(data["cases"], list):
        rows = data["cases"]
    else:
        rows = []

    cases: list[Case] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        cases.append(
            Case(
                input=str(row["input"]),
                expected=(str(row["expected"]) if row.get("expected") is not None else None),
            )
        )
    return cases


def load_config(path: str | Path) -> Config:
    config_path = Path(path).resolve()
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("config must be a YAML mapping")

    config_dir = config_path.parent
    target = data.get("target")
    if not isinstance(target, dict):
        raise ValueError("config requires a 'target' mapping")

    threshold_data = data.get("threshold") or {}
    threshold = Threshold(
        mode=str(threshold_data.get("mode", "absolute")),
        max_drop=float(threshold_data.get("max_drop", 0.0)),
    )

    evaluators = data.get("evaluators")
    if not isinstance(evaluators, list) or not evaluators:
        evaluators = [{"type": "exact_match"}]

    baseline = config_dir / str(data["baseline"]) if data.get("baseline") else None

    return Config(
        name=str(data.get("name", "litmus")),
        target=target,
        cases=_load_cases(data, config_dir),
        evaluators=[e for e in evaluators if isinstance(e, dict)],
        repeats=int(data.get("repeats", 1)),
        seed=int(data.get("seed", 1234)),
        threshold=threshold,
        config_dir=config_dir,
        baseline=baseline,
    )
