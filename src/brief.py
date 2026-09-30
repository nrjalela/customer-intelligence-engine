"""Stage 3: generate the executive weekly brief with Prompt C."""

import json
from datetime import date

from prompts.prompts import PROMPT_C
from src.llm import PROJECT_ROOT, call_claude

MAX_TOKENS = 600
REPORTS_DIR = PROJECT_ROOT / "reports"


def generate_brief(themes: list[dict]) -> str:
    """Run Prompt C on the theme clusters, save the brief to reports/, and return it.

    The report is written to ``reports/weekly_brief_{YYYY-MM-DD}.md``.
    """
    prompt = PROMPT_C.format(themes=json.dumps(themes, indent=1))
    brief = call_claude(prompt, MAX_TOKENS)

    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / f"weekly_brief_{date.today().isoformat()}.md"
    path.write_text(brief + "\n", encoding="utf-8")
    return brief
