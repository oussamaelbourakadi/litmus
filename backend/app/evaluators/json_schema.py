"""JsonSchema — pass if the output is JSON conforming to a schema."""

from __future__ import annotations

import json
from typing import Any

from jsonschema import Draft202012Validator

from app.evaluators.base import EvalCase, EvalScore, Evaluator, evaluator_registry


@evaluator_registry.register("json_schema")
class JsonSchema(Evaluator):
    name = "json_schema"

    def __init__(self, schema: dict[str, Any]) -> None:
        self._validator = Draft202012Validator(schema)

    async def score(self, case: EvalCase, output: str) -> EvalScore:
        try:
            data = json.loads(output)
        except json.JSONDecodeError as exc:
            return EvalScore(0.0, False, f"invalid JSON: {exc.msg}")

        error = next(self._validator.iter_errors(data), None)
        if error is not None:
            return EvalScore(0.0, False, error.message)
        return EvalScore(1.0, True, None)
