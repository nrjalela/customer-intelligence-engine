"""Shared Claude API helpers used by the analyze, cluster and brief stages."""

import json
import os
import re
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

MODEL = "claude-sonnet-4-6"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

_client = None


def get_client() -> Anthropic:
    """Return a cached Anthropic client, loading the API key from the environment."""
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Add it to the .env file in the project root."
            )
        _client = Anthropic(api_key=api_key)
    return _client


def call_claude(prompt: str, max_tokens: int) -> str:
    """Send a single-turn prompt to Claude and return the response text."""
    response = get_client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text").strip()


def parse_json(text: str):
    """Parse JSON from a model response, tolerating markdown fences and stray prose.

    Raises ``json.JSONDecodeError`` if no valid JSON can be recovered.
    """
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fall back to the outermost array or object embedded in the text.
        for opener, closer in (("[", "]"), ("{", "}")):
            start, end = cleaned.find(opener), cleaned.rfind(closer)
            if start != -1 and end > start:
                try:
                    return json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    continue
        raise
