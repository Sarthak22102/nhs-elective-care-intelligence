import pytest
from nhs_elective_intelligence.analytics.pressure import elective_pressure_score, score_sensitivity


def test_equal_weight_pressure_score_is_explainable():
    score,contrib=elective_pressure_score({"a":1.0,"b":0.5,"c":0.0,"d":0.5},min_components=4)
    assert score==50.0 and round(sum(contrib.values()),10)==score

def test_missing_components_do_not_become_zero():
    score,contrib=elective_pressure_score({"a":1.0,"b":None,"c":0.2},min_components=3)
    assert score is None and contrib=={}

def test_invalid_percentile_rejected():
    with pytest.raises(ValueError): elective_pressure_score({"a":1.2,"b":0.5,"c":0.3,"d":0.4},min_components=4)

def test_custom_weights_normalised():
    score,_=elective_pressure_score({"a":1,"b":0,"c":0,"d":0},weights={"a":4,"b":2,"c":2,"d":2},min_components=4)
    assert score==40

def test_sensitivity_returns_one_score_per_scenario():
    assert len(score_sensitivity({"a":0.8,"b":0.4,"c":0.2,"d":0.6},[{"a":1,"b":1,"c":1,"d":1},{"a":2,"b":1,"c":1,"d":1}]))==2
