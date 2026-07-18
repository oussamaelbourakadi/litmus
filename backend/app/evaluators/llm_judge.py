"""LLMJudge — score an output against a textual rubric using any provider.

The judge model is asked to return a JSON object ``{"score": <0..1>, "reason":
<string>}``. Parsing is robust: it extracts the JSON object even if surrounded
by prose, and falls back to the first float in the text. Using the deterministic
MockProvider makes judge behaviour reproducible in tests.
"""

from __future__ import annotations

import json
import re

from app.evaluators.base import EvalCase, EvalScore, Evaluator, evaluator_registry
from app.providers.base import ModelProvider, ProviderConfig

_FLOAT_RE = re.compile(r"[-+]?\d*\.?\d+")

_PROMPT_TEMPLATE = (
    "You are an impartial evaluator. Rate how well the RESPONSE satisfies the "
    "CRITERION on a scale from 0 to 1.\n"
    'Return ONLY a JSON object: {{"score": <float between 0 and 1>, "reason": <short string>}}.\n\n'
    "CRITERION:\n{rubric}\n\n"
    "{expected_block}"
    "RESPONSE:\n{output}\n"
)


def _clamp(value: float) -> float:
    return min(1.0, max(0.0, value))


@evaluator_registry.register("llm_judge")
class LLMJudge(Evaluator):
    name = "llm_judge"

    def __init__(
        self,
        provider: ModelProvider,
        rubric: str,
        *,
        threshold: float = 0.5,
        config: ProviderConfig | None = None,
    ) -> None:
        self._provider = provider
        self._rubric = rubric
        self._threshold = threshold
        self._config = config or ProviderConfig()

    async def score(self, case: EvalCase, output: str) -> EvalScore:
        prompt = self._build_prompt(case, output)
        result = await self._provider.generate(prompt, self._config)
        value, reason = self._parse(result.text)
        return EvalScore(value=value, passed=value >= self._threshold, reason=reason)

    def _build_prompt(self, case: EvalCase, output: str) -> str:
        expected_block = (
            f"REFERENCE ANSWER:\n{case.expected}\n\n" if case.expected is not None else ""
        )
        return _PROMPT_TEMPLATE.format(
            rubric=self._rubric, expected_block=expected_block, output=output
        )

    @staticmethod
    def _parse(text: str) -> tuple[float, str | None]:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            data = json.loads(text[start:end])
            value = _clamp(float(data["score"]))
            reason = data.get("reason")
            return value, (str(reason) if reason is not None else None)
        except (ValueError, KeyError, TypeError):
            pass

        match = _FLOAT_RE.search(text)
        if match is not None:
            return _clamp(float(match.group())), None
        return 0.0, "could not parse judge output"
