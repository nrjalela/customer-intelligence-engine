"""Streamlit dashboard for the AI Customer Intelligence Engine."""

from datetime import date

import pandas as pd
import streamlit as st

from src.analyze import analyze_reviews
from src.brief import generate_brief
from src.cluster import cluster_themes
from src.ingest import load_reviews

IMPACT_COLORS = {"high": "#d64545", "medium": "#e6a23c", "low": "#3fa66b"}

st.set_page_config(page_title="Customer Intelligence Engine", page_icon="📊", layout="wide")
st.title("Customer Intelligence Engine")
st.caption("Feedback → sentiment & insights → themes → executive brief")


def impact_badge(impact: str) -> str:
    """Return an HTML badge coloured by business impact level."""
    level = str(impact).lower()
    color = IMPACT_COLORS.get(level, "#888888")
    return (
        f"<span style='background:{color};color:white;padding:2px 10px;"
        f"border-radius:12px;font-size:0.8rem;font-weight:600'>{level.upper()} IMPACT</span>"
    )


def run_pipeline(reviews: list[dict]) -> None:
    """Chain analyze → cluster → brief, updating progress indicators and session state."""
    progress = st.progress(0.0, text="Stage 1/3 — analyzing reviews…")

    def on_progress(done: int, total: int) -> None:
        progress.progress(done / total * 0.6, text=f"Stage 1/3 — analyzed {done}/{total} reviews")

    with st.status("Running pipeline…", expanded=True) as status:
        try:
            st.write("Stage 1/3: analyzing each review…")
            analyzed = analyze_reviews(reviews, progress_callback=on_progress)
            st.write(f"✅ Analyzed {len(analyzed)} reviews")

            progress.progress(0.6, text="Stage 2/3 — clustering themes…")
            st.write("Stage 2/3: clustering themes…")
            themes = cluster_themes(analyzed)
            st.write(f"✅ Found {len(themes)} themes")

            progress.progress(0.85, text="Stage 3/3 — writing executive brief…")
            st.write("Stage 3/3: writing executive brief…")
            brief = generate_brief(themes)
            st.write("✅ Brief saved to reports/")
        except Exception as exc:  # surface any API/parse error in the UI
            status.update(label="Pipeline failed", state="error")
            progress.empty()
            st.error(f"{type(exc).__name__}: {exc}")
            return
        status.update(label="Pipeline complete", state="complete", expanded=False)

    progress.progress(1.0, text="Done")
    st.session_state.update(analyzed=analyzed, themes=themes, brief=brief, brief_date=date.today().isoformat())


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload reviews CSV", type="csv")
    st.caption("Columns: id, date, source, product_area, review_text, rating")
    if st.button("Use sample data", use_container_width=True):
        st.session_state["use_sample"] = True
    if uploaded is not None:
        st.session_state["use_sample"] = False

reviews, load_error = None, None
try:
    if uploaded is not None:
        reviews = load_reviews(uploaded)
    elif st.session_state.get("use_sample"):
        reviews = load_reviews()
except Exception as exc:
    load_error = f"Could not load data: {exc}"

with st.sidebar:
    if load_error:
        st.error(load_error)
    elif reviews is not None:
        st.success(f"{len(reviews)} reviews loaded")
    else:
        st.info("Upload a CSV or click “Use sample data”.")
    run_clicked = st.button(
        "▶ Run pipeline", type="primary", use_container_width=True, disabled=reviews is None
    )

if run_clicked and reviews is not None:
    run_pipeline(reviews)

# ------------------------------------------------------------------- tabs
tab_raw, tab_themes, tab_brief = st.tabs(["Raw Analysis", "Theme Clusters", "Executive Brief"])

with tab_raw:
    if "analyzed" in st.session_state:
        df = pd.DataFrame(st.session_state["analyzed"])
        cols = ["id", "date", "source", "product_area", "rating", "sentiment",
                "intensity", "urgency", "pain_point", "feature_mentioned", "review_text"]
        st.dataframe(df[[c for c in cols if c in df.columns]], use_container_width=True, hide_index=True)
        n_failed = int(df.get("parse_error", pd.Series(dtype=bool)).sum())
        if n_failed:
            st.warning(f"{n_failed} review(s) could not be parsed and use fallback values.")
    else:
        st.info("Run the pipeline to see per-review analysis.")

with tab_themes:
    if "themes" in st.session_state:
        for theme in st.session_state["themes"]:
            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.subheader(theme.get("theme_name", "Untitled theme"))
                right.markdown(impact_badge(theme.get("business_impact", "unknown")), unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("Mentions", theme.get("frequency_count", "–"))
                m2.metric("Avg intensity", theme.get("avg_intensity", "–"))
                for quote in theme.get("representative_quotes", []):
                    st.markdown(f"> “{quote}”")
                st.markdown(f"**Recommended action:** {theme.get('recommended_action', '–')}")
    else:
        st.info("Run the pipeline to see theme clusters.")

with tab_brief:
    if "brief" in st.session_state:
        st.markdown(st.session_state["brief"])
        st.download_button(
            "Download brief (.md)",
            data=st.session_state["brief"],
            file_name=f"weekly_brief_{st.session_state['brief_date']}.md",
            mime="text/markdown",
        )
    else:
        st.info("Run the pipeline to generate the executive brief.")
