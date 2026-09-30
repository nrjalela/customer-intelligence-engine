"""Stage 1: analyze each feedback item with Prompt A."""

import json
from typing import Callable, Optional

from prompts.prompts import PROMPT_A
from src.llm import call_claude, parse_json

MAX_TOKENS = 300

FALLBACK_ANALYSIS = {
    "sentiment": "neutral",
    "intensity": 5,
    "pain_point": None,
    "feature_mentioned": None,
    "urgency": "low",
}


def _normalize(parsed: dict) -> dict:
    """Coerce a parsed model response into the expected schema with safe defaults."""
    result = dict(FALLBACK_ANALYSIS)
    for key in result:
        if key in parsed:
            result[key] = parsed[key]
    sentiment = str(result["sentiment"]).lower()
    result["sentiment"] = sentiment if sentiment in {"positive", "neutral", "negative"} else "neutral"
    urgency = str(result["urgency"]).lower()
    result["urgency"] = urgency if urgency in {"high", "medium", "low"} else "low"
    try:
        result["intensity"] = max(1, min(10, int(result["intensity"])))
    except (TypeError, ValueError):
        result["intensity"] = FALLBACK_ANALYSIS["intensity"]
    return result


def analyze_review(review: dict) -> dict:
    """Run Prompt A on one review and return the review merged with its analysis.

    If the response cannot be parsed as JSON, a neutral fallback analysis is
    used and ``parse_error`` is set to True so the row stays visible downstream.
    """
    raw = call_claude(PROMPT_A.format(text=review["review_text"]), MAX_TOKENS)
    try:
        parsed = parse_json(raw)
        if not isinstance(parsed, dict):
            raise ValueError("expected a JSON object")
        analysis, parse_error = _normalize(parsed), False
    except (json.JSONDecodeError, ValueError):
        analysis, parse_error = dict(FALLBACK_ANALYSIS), True
    return {**review, **analysis, "parse_error": parse_error}


def analyze_reviews(
    reviews: list[dict], progress_callback: Optional[Callable[[int, int], None]] = None
) -> list[dict]:
    """Analyze every review sequentially and return the list of result dicts.

    ``progress_callback(done, total)`` is called after each review if provided.
    """
    results = []
    for i, review in enumerate(reviews, start=1):
        results.append(analyze_review(review))
        if progress_callback:
            progress_callback(i, len(reviews))
    return results
