"""Inequality measures that propagate suppression/missingness safely."""
from __future__ import annotations

from nhs_elective_intelligence.cleaning.suppression import PublishedValue, eligible_for_precise_calculation


def absolute_gap(group_a: PublishedValue, group_b: PublishedValue) -> float | None:
    if not eligible_for_precise_calculation(group_a, group_b):
        return None
    return float(group_a.value) - float(group_b.value)


def relative_ratio(group_a: PublishedValue, group_b: PublishedValue) -> float | None:
    if not eligible_for_precise_calculation(group_a, group_b):
        return None
    if group_b.value == 0:
        return None
    return float(group_a.value) / float(group_b.value)
