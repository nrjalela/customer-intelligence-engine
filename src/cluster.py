"""Stage 2: cluster analyzed feedback into recurring themes with Prompt B."""

import json

from prompts.prompts import PROMPT_B
from src.llm import call_claude, parse_json

MAX_TOKENS = 1000

BATCH_FIELDS = [
    "id", "product_area", "review_text", "sentiment", "intensity",
    "pain_point", "feature_mentioned", "urgency",
]


def cluster_themes(analyzed: list[dict]) -> list[dict]:
    """Run Prompt B over the full analyzed batch and return the theme cluster list.

    Raises ``ValueError`` if the model response is not a JSON array of themes.
    """
    batch = [{k: item.get(k) for k in BATCH_FIELDS} for item in analyzed]
    prompt = PROMPT_B.format(n=len(batch), batch=json.dumps(batch, indent=1))
    raw = call_claude(prompt, MAX_TOKENS)

    try:
        themes = parse_json(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse theme clusters from model output: {raw[:200]!r}") from exc

    if isinstance(themes, dict):  # tolerate {"themes": [...]}
        themes = next((v for v in themes.values() if isinstance(v, list)), None)
    if not isinstance(themes, list):
        raise ValueError("Theme clustering did not return a JSON array.")
    return themes
