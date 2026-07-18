"""A tiny deterministic target for the Litmus demo (no API key)."""

ANSWERS = {
    "capital of France?": "Paris",
    "2+2?": "4",
    "color of the sky?": "blue",
}


def answer(prompt: str) -> str:
    return ANSWERS.get(prompt.strip(), "I don't know")
