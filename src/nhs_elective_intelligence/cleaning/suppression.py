"""Suppression-aware parsing for published NHS aggregate counts.

The parser intentionally preserves disclosure-control states instead of turning
masked cells into zero or attempting reconstruction.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math
from typing import Any


class ValueStatus(StrEnum):
    OBSERVED = "observed"
    SUPPRESSED = "suppressed"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class PublishedValue:
    value: float | None
    status: ValueStatus
    raw: Any = None


SUPPRESSION_TOKENS = {"*", "suppressed", "s", "<8", "1-7"}
NA_TOKENS = {"n/a", "na", "not applicable", "not_applicable"}
MISSING_TOKENS = {"", "-", "..", "null", "none", "nan"}


def parse_published_count(raw: Any) -> PublishedValue:
    """Parse one published aggregate value without defeating suppression.

    Numeric zero is an observed zero. Suppressed/masked values remain ``None``
    with a separate status and must not be included in ratios/rankings that
    would imply false precision.
    """
    if raw is None:
        return PublishedValue(None, ValueStatus.MISSING, raw)
    if isinstance(raw, float) and math.isnan(raw):
        return PublishedValue(None, ValueStatus.MISSING, raw)
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return PublishedValue(float(raw), ValueStatus.OBSERVED, raw)

    text = str(raw).strip()
    lower = text.lower()
    if lower in SUPPRESSION_TOKENS:
        return PublishedValue(None, ValueStatus.SUPPRESSED, raw)
    if lower in NA_TOKENS:
        return PublishedValue(None, ValueStatus.NOT_APPLICABLE, raw)
    if lower in MISSING_TOKENS:
        return PublishedValue(None, ValueStatus.MISSING, raw)

    cleaned = text.replace(",", "")
    try:
        return PublishedValue(float(cleaned), ValueStatus.OBSERVED, raw)
    except ValueError:
        return PublishedValue(None, ValueStatus.MISSING, raw)


def eligible_for_precise_calculation(*values: PublishedValue) -> bool:
    return all(v.status == ValueStatus.OBSERVED and v.value is not None for v in values)
