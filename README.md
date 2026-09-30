# AI Customer Intelligence Engine

A 3-stage Claude-powered pipeline that turns raw customer feedback into an executive-ready weekly brief.

## Architecture

```
  ┌──────────────────┐
  │ CSV of feedback  │  reviews, app store, support tickets
  └────────┬─────────┘
           │  src/ingest.py — load + clean
           ▼
  ┌──────────────────┐   Prompt A, one Claude call per review
  │ STAGE 1: Analyze │──► sentiment · intensity · pain point · feature · urgency
  └────────┬─────────┘   src/analyze.py
           │
           ▼
  ┌──────────────────┐   Prompt B, one Claude call on the full batch
  │ STAGE 2: Cluster │──► top 5 themes · frequency · impact · recommended action
  └────────┬─────────┘   src/cluster.py
           │
           ▼
  ┌──────────────────┐   Prompt C, one Claude call
  │ STAGE 3: Brief   │──► 300-word executive brief → reports/weekly_brief_<date>.md
  └────────┬─────────┘   src/brief.py
           │
           ▼
  ┌──────────────────┐
  │ Streamlit app.py │  Raw Analysis · Theme Clusters · Executive Brief
  └──────────────────┘
```

## Setup

```bash
git clone <your-repo-url>
cd customer-intelligence-engine
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your-key-here" > .env
streamlit run app.py
```

Then click **Use sample data** (or upload your own CSV) and **Run pipeline**.

CSV columns: `id, date, source, product_area, review_text, rating`.

## Screenshot

![Dashboard screenshot](docs/screenshot.png)

<!-- Replace with a real screenshot after your first run. -->

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Anthropic](https://img.shields.io/badge/Claude_API-D97757?logo=anthropic&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)

## Project Layout

| Path | Purpose |
|------|---------|
| `prompts/prompts.py` | The three prompt templates |
| `src/ingest.py` | CSV loading and cleaning |
| `src/analyze.py` | Per-review analysis (Prompt A) |
| `src/cluster.py` | Theme clustering (Prompt B) |
| `src/brief.py` | Executive brief generation (Prompt C) |
| `src/llm.py` | Shared Claude client and JSON parsing helpers |
| `reports/` | Generated briefs (gitignored) |
