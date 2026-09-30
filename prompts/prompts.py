"""Prompt templates for the three pipeline stages.

All templates are used with ``str.format``, so literal JSON braces are doubled
(``{{`` / ``}}``). Only the named placeholders (``{text}``, ``{n}``, ``{batch}``,
``{themes}``) are substituted.
"""

PROMPT_A = """You are a customer insight analyst. Analyze this single customer feedback item.
Feedback: {text}
Extract as JSON only:
{{ "sentiment": "positive|neutral|negative", "intensity": 1-10, "pain_point": "one-line or null", "feature_mentioned": "product area or null", "urgency": "high|medium|low" }}
Return JSON only. No commentary."""

PROMPT_B = """You are a strategic customer insights lead. Below are {n} analyzed feedback items as JSON.
{batch}
Identify the top 5 recurring themes. For each output as JSON array:
[ {{ "theme_name": "...", "frequency_count": 0, "avg_intensity": 0.0, "representative_quotes": ["...", "..."], "business_impact": "high|medium|low", "recommended_action": "..." }} ]
JSON only."""

PROMPT_C = """You are a Chief Customer Officer writing a weekly brief for a non-technical executive team.
Themes this week: {themes}
Write a 300-word strategic brief. Structure:
1. One headline insight — the most urgent thing to act on
2. Top 3 themes in plain business language (no jargon)
3. One risk flag
4. One recommended action this week
Tone: confident, direct. No bullet soup."""
