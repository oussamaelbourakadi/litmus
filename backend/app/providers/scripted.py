"""ScriptedProvider — a deterministic fixture model with a built-in demo Q&A bank.

It answers a curated set of questions from its own knowledge (no network, no key),
so an evaluation against matching expected answers genuinely passes. A "weak" model
tier (name contains small/mini/…) deterministically misses the questions marked
hard, so two runs (e.g. ``mock-small`` vs ``mock-large``) produce a real,
reproducible accuracy difference — ideal for a portfolio demo where the numbers are
computed by the app itself, not faked.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from app.providers.base import (
    GenerateResult,
    ModelProvider,
    ProviderConfig,
    Usage,
    provider_registry,
)


@dataclass(frozen=True, slots=True)
class _QA:
    question: str
    answer: str
    hard: bool = False
    distractor: str = ""


# The fixture model's "knowledge". The demo dataset uses these exact questions.
_BANK: tuple[_QA, ...] = (
    _QA("What is the capital of France?", "Paris"),
    _QA("What is 2 + 2?", "4"),
    _QA("What is the capital of Japan?", "Tokyo"),
    _QA("What color do you get by mixing blue and yellow?", "Green"),
    _QA("What is 10 * 5?", "50"),
    _QA("What is the largest planet in our solar system?", "Jupiter"),
    _QA("What is the chemical symbol for water?", "H2O", hard=True, distractor="HO"),
    _QA("How many continents are there?", "7"),
    _QA("What is the capital of Italy?", "Rome"),
    _QA("What is 100 / 4?", "25"),
    _QA("What language is primarily spoken in Brazil?", "Portuguese"),
    _QA("What is the square root of 81?", "9", hard=True, distractor="8"),
)

_BY_QUESTION = {qa.question.strip().casefold(): qa for qa in _BANK}

# Simulated system-prompt overhead so cost is realistic (and non-zero).
_SYSTEM_PROMPT_TOKENS = 24
_WEAK_TAGS = ("small", "mini", "7b", "v1", "lite")


def _is_weak(model: str) -> bool:
    lowered = model.lower()
    return any(tag in lowered for tag in _WEAK_TAGS)


def _latency_ms(prompt: str, model: str) -> float:
    """Deterministic, model-dependent latency (larger models are slower)."""
    base = 45.0 if _is_weak(model) else 180.0
    jitter = int(hashlib.sha256(f"{model}:{prompt}".encode()).hexdigest()[:4], 16) % 90
    return base + jitter


@provider_registry.register("scripted")
class ScriptedProvider(ModelProvider):
    name = "scripted"

    async def generate(self, prompt: str, config: ProviderConfig) -> GenerateResult:
        qa = _BY_QUESTION.get(prompt.strip().casefold())
        if qa is None:
            text = "I don't know"
        elif qa.hard and _is_weak(config.model):
            text = qa.distractor or "I'm not sure"
        else:
            text = qa.answer

        usage = Usage(
            prompt_tokens=_SYSTEM_PROMPT_TOKENS + len(prompt.split()),
            completion_tokens=max(1, len(text.split())),
        )
        return GenerateResult(text=text, usage=usage, latency_ms=_latency_ms(prompt, config.model))
