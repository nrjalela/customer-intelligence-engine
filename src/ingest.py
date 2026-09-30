"""Stage 0: load and clean customer feedback from CSV."""

from pathlib import Path

import pandas as pd

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_reviews.csv"
REQUIRED_COLUMNS = ["id", "date", "source", "product_area", "review_text", "rating"]


def load_reviews(source=DEFAULT_PATH) -> list[dict]:
    """Load a reviews CSV (path or file-like object), clean nulls, return a list of dicts.

    Rows with no review text are dropped. Missing ids are filled sequentially,
    missing text metadata becomes "unknown", and missing ratings become None.
    """
    df = pd.read_csv(source)
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")

    df = df[REQUIRED_COLUMNS].copy()
    df["review_text"] = df["review_text"].astype("string").str.strip()
    df = df[df["review_text"].notna() & (df["review_text"] != "")]

    for col in ("source", "product_area"):
        df[col] = df[col].fillna("unknown").astype(str).str.strip().str.lower()
    df["date"] = df["date"].fillna("").astype(str)
    df["review_text"] = df["review_text"].astype(str)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    df = df.reset_index(drop=True)
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["id"] = df["id"].fillna(pd.Series(range(1, len(df) + 1))).astype(int)

    # Convert NaN ratings to None so the records are JSON-serialisable.
    records = df.astype(object).where(df.notna(), None).to_dict(orient="records")
    return records
