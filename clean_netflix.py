"""
Netflix titles: light cleaning + feature engineering for the EDA notebook
========================================================================

    python src/clean_netflix.py

Reads  data/raw/netflix_titles.csv
Writes data/processed/netflix_titles_clean.csv

The raw file is already fairly tidy, so cleaning is deliberately conservative:
we repair what is demonstrably wrong, keep genuine missing values as missing,
and add columns that make the analysis easier (parsed dates, numeric duration,
primary country / genre, rating groups).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "netflix_titles.csv"
CLEAN_PATH = ROOT / "data" / "processed" / "netflix_titles_clean.csv"

# Content-rating -> audience group (US TV Parental Guidelines + MPA)
RATING_GROUPS = {
    "TV-Y": "Kids", "TV-Y7": "Kids", "TV-Y7-FV": "Kids", "TV-G": "Kids", "G": "Kids",
    "TV-PG": "Older kids / family", "PG": "Older kids / family",
    "TV-14": "Teens", "PG-13": "Teens",
    "TV-MA": "Adults", "R": "Adults", "NC-17": "Adults",
    "Not Rated": "Not rated",
}
GROUP_ORDER = ["Kids", "Older kids / family", "Teens", "Adults", "Not rated"]

TEXT_COLS = ["show_id", "type", "title", "director", "cast", "country", "date_added",
             "rating", "duration", "listed_in", "description"]


def _collapse(s: pd.Series) -> pd.Series:
    return s.str.replace(r"\s+", " ", regex=True).str.strip()


def _split_list(s: pd.Series) -> pd.Series:
    """'A, B,' -> ['A', 'B'] (drops empty fragments, e.g. trailing commas)."""
    return s.map(lambda x: [p.strip() for p in x.split(",") if p.strip()] if isinstance(x, str) else [])


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    # 1. whitespace --------------------------------------------------------
    for col in TEXT_COLS:
        df[col] = _collapse(df[col])

    # 2. three Louis C.K. specials have their runtime in `rating` -------------
    shifted = df["rating"].str.fullmatch(r"\d+ min", na=False) & df["duration"].isna()
    df.loc[shifted, "duration"] = df.loc[shifted, "rating"]
    df.loc[shifted, "rating"] = np.nan

    # 3. ratings -----------------------------------------------------------
    df["rating"] = df["rating"].replace({"NR": "Not Rated", "UR": "Not Rated"})
    df["rating_group"] = pd.Categorical(
        df["rating"].map(RATING_GROUPS), categories=GROUP_ORDER, ordered=True
    )

    # 4. dates -------------------------------------------------------------
    df["date_added"] = pd.to_datetime(df["date_added"], format="%B %d, %Y")
    df["added_year"] = df["date_added"].dt.year.astype("Int64")
    df["added_month"] = df["date_added"].dt.month.astype("Int64")
    # negative values are real: Netflix lists some titles before their release year
    df["release_to_add_years"] = (df["added_year"] - df["release_year"]).astype("Int64")

    # 5. duration -> numeric ------------------------------------------------
    num = df["duration"].str.extract(r"(\d+)")[0].astype("Float64")
    df["duration_min"] = num.where(df["type"] == "Movie").astype("Int64")
    df["n_seasons"] = num.where(df["type"] == "TV Show").astype("Int64")

    # 6. multi-valued columns ----------------------------------------------
    countries = _split_list(df["country"])
    genres = _split_list(df["listed_in"])
    cast = _split_list(df["cast"])
    df["country"] = countries.map(", ".join).replace("", np.nan)      # drops trailing commas
    df["primary_country"] = countries.map(lambda l: l[0] if l else np.nan)
    df["n_countries"] = countries.map(len).astype("int64")
    df["primary_genre"] = genres.map(lambda l: l[0] if l else np.nan)
    df["n_genres"] = genres.map(len).astype("int64")
    df["n_cast"] = cast.map(len).astype("int64")

    # 7. column order -------------------------------------------------------
    first = ["show_id", "type", "title", "director", "cast", "country", "primary_country",
             "date_added", "added_year", "added_month", "release_year", "release_to_add_years",
             "rating", "rating_group", "duration", "duration_min", "n_seasons",
             "listed_in", "primary_genre", "n_genres", "n_countries", "n_cast", "description"]
    return df[first]


def main() -> None:
    raw = pd.read_csv(RAW_PATH)
    df = clean(raw)
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Saved {len(df):,} rows x {df.shape[1]} cols -> {CLEAN_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
