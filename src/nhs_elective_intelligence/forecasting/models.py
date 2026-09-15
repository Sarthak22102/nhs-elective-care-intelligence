"""Interpretable time-series baselines with explicit sufficiency gates."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ForecastReadiness:
    ready: bool
    observations: int
    reason: str


def assess_forecast_readiness(series: pd.Series, minimum_months: int = 24) -> ForecastReadiness:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    n = len(clean)
    if n < minimum_months:
        return ForecastReadiness(False, n, f"Need at least {minimum_months} valid monthly observations; found {n}.")
    if clean.nunique() < 4:
        return ForecastReadiness(False, n, "Series has too little variation for useful model comparison.")
    return ForecastReadiness(True, n, "Sufficient history for time-based baseline comparison.")


def naive_forecast(train: pd.Series, horizon: int) -> np.ndarray:
    clean = pd.to_numeric(train, errors="coerce").dropna()
    if clean.empty:
        raise ValueError("Training series is empty.")
    return np.repeat(float(clean.iloc[-1]), horizon)


def seasonal_naive_forecast(train: pd.Series, horizon: int, season: int = 12) -> np.ndarray:
    clean = pd.to_numeric(train, errors="coerce").dropna().to_numpy(dtype=float)
    if len(clean) < season:
        raise ValueError("Seasonal naive requires at least one complete season.")
    pattern = clean[-season:]
    return np.array([pattern[i % season] for i in range(horizon)], dtype=float)


def error_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if actual.shape != predicted.shape:
        raise ValueError("Actual and predicted arrays must have the same shape.")
    error = predicted - actual
    mae = float(np.mean(np.abs(error)))
    rmse = float(np.sqrt(np.mean(error**2)))
    denom = np.abs(actual) + np.abs(predicted)
    smape = float(np.mean(np.where(denom == 0, 0, 2 * np.abs(error) / denom)))
    return {"mae": mae, "rmse": rmse, "smape": smape}
