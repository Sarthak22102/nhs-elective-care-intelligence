"""Shared cleaning helpers."""
from __future__ import annotations

import re
import pandas as pd


def canonical_column(name: object) -> str:
    text = str(name).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def canonicalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [canonical_column(c) for c in out.columns]
    return out


def parse_reporting_month(value: object) -> pd.Timestamp:
    """Return month-end Timestamp; raise on invalid dates rather than guessing."""
    ts = pd.to_datetime(value, errors="raise")
    return ts.to_period("M").to_timestamp("M")


def normalise_code(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip().upper()
    return text or None
