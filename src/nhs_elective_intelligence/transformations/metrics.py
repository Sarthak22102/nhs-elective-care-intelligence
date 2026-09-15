"""Transparent elective-care metric calculations."""
from __future__ import annotations

import math
import pandas as pd


def safe_divide(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator is None:
        return None
    try:
        if math.isnan(float(numerator)) or math.isnan(float(denominator)):
            return None
    except (TypeError, ValueError):
        return None
    if float(denominator) == 0:
        return None
    return float(numerator) / float(denominator)


def completed_pathways(admitted: float | None, non_admitted: float | None) -> float | None:
    if admitted is None or non_admitted is None:
        return None
    return float(admitted) + float(non_admitted)


def demand_throughput_ratio(new_pathways: float | None, completed: float | None) -> float | None:
    return safe_divide(new_pathways, completed)


def clearance_ratio(new_pathways: float | None, completed: float | None) -> float | None:
    return safe_divide(completed, new_pathways)


def net_pathway_pressure(new_pathways: float | None, completed: float | None) -> float | None:
    if new_pathways is None or completed is None:
        return None
    return float(new_pathways) - float(completed)


def wait_rate(wait_count: float | None, total_incomplete: float | None) -> float | None:
    return safe_divide(wait_count, total_incomplete)


def backlog_per_monthly_completion(backlog: float | None, completed: float | None) -> float | None:
    """Scenario ratio, not a forecast of time to clear."""
    return safe_divide(backlog, completed)


def rolling_sum(series: pd.Series, window: int = 3) -> pd.Series:
    return series.rolling(window=window, min_periods=window).sum()


def rolling_mean(series: pd.Series, window: int = 3) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def pct_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous is None or float(previous) == 0:
        return None
    return (float(current) - float(previous)) / float(previous)
