from nhs_elective_intelligence.analytics.inequality import absolute_gap, relative_ratio
from nhs_elective_intelligence.cleaning.suppression import parse_published_count


def test_observed_gap_and_ratio():
    a=parse_published_count(150); b=parse_published_count(100)
    assert absolute_gap(a,b)==50
    assert relative_ratio(a,b)==1.5


def test_suppression_propagates_to_inequality_measure():
    a=parse_published_count("*"); b=parse_published_count(100)
    assert absolute_gap(a,b) is None
    assert relative_ratio(a,b) is None


def test_zero_denominator_ratio_is_none():
    assert relative_ratio(parse_published_count(5),parse_published_count(0)) is None
