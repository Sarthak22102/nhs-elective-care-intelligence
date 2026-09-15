"""Explainable composite-pressure utilities.

The project does not publish a pressure score unless the full underlying facts
(backlog, long waits, demand, throughput and growth) pass the quality gate.
"""
from __future__ import annotations

from collections.abc import Mapping
import numpy as np

DEFAULT_COMPONENTS = (
    "backlog_to_throughput_percentile",
    "backlog_growth_percentile",
    "long_wait_rate_percentile",
    "demand_throughput_percentile",
    "backlog_acceleration_percentile",
)


def elective_pressure_score(
    components: Mapping[str, float | None],
    weights: Mapping[str, float] | None = None,
    min_components: int = 4,
) -> tuple[float | None, dict[str, float]]:
    """Return 0-100 equal/custom weighted score plus component contributions.

    Inputs must already be percentile-normalised to [0, 1]. Missing components
    are not silently converted to zero. At least ``min_components`` are needed.
    """
    valid = {k: float(v) for k, v in components.items() if v is not None and np.isfinite(v)}
    if len(valid) < min_components:
        return None, {}
    if any(v < 0 or v > 1 for v in valid.values()):
        raise ValueError("Pressure components must be percentile-normalised to [0, 1].")

    if weights is None:
        raw_weights = {k: 1.0 for k in valid}
    else:
        raw_weights = {k: float(weights[k]) for k in valid if k in weights}
        if set(raw_weights) != set(valid):
            raise ValueError("Every included pressure component requires a weight.")
        if any(w < 0 for w in raw_weights.values()):
            raise ValueError("Pressure weights cannot be negative.")
    denom = sum(raw_weights.values())
    if denom <= 0:
        raise ValueError("Pressure weights must sum to a positive value.")

    norm_weights = {k: w / denom for k, w in raw_weights.items()}
    contributions = {k: valid[k] * norm_weights[k] * 100 for k in valid}
    return sum(contributions.values()), contributions


def score_sensitivity(components: Mapping[str, float], weight_scenarios: list[Mapping[str, float]]) -> list[float]:
    scores: list[float] = []
    for scenario in weight_scenarios:
        score, _ = elective_pressure_score(components, scenario, min_components=len(components))
        if score is not None:
            scores.append(score)
    return scores
