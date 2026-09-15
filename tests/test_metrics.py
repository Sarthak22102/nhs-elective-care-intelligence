import pandas as pd

from nhs_elective_intelligence.transformations.metrics import (
    backlog_per_monthly_completion, clearance_ratio, completed_pathways,
    demand_throughput_ratio, net_pathway_pressure, pct_change, rolling_sum, safe_divide,
)


def test_safe_divide_zero_denominator_returns_none(): assert safe_divide(10,0) is None

def test_completed_pathways_requires_both_components():
    assert completed_pathways(80,120)==200
    assert completed_pathways(None,120) is None

def test_demand_throughput_and_clearance_are_reciprocal_for_positive_values():
    assert demand_throughput_ratio(120,100)==1.2
    assert clearance_ratio(120,100)==100/120

def test_net_pressure(): assert net_pathway_pressure(120,100)==20

def test_backlog_per_completion_is_scenario_ratio(): assert backlog_per_monthly_completion(600,200)==3

def test_pct_change_handles_zero_baseline():
    assert pct_change(20,0) is None
    assert pct_change(110,100)==0.1

def test_rolling_sum_requires_full_window():
    out=rolling_sum(pd.Series([1,2,3,4]),3)
    assert pd.isna(out.iloc[1]); assert out.iloc[2]==6; assert out.iloc[3]==9
