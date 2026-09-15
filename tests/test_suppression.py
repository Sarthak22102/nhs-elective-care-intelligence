from nhs_elective_intelligence.cleaning.suppression import ValueStatus, eligible_for_precise_calculation, parse_published_count


def test_zero_is_observed_not_suppressed():
    parsed=parse_published_count(0); assert parsed.value==0 and parsed.status==ValueStatus.OBSERVED

def test_star_is_suppressed():
    parsed=parse_published_count("*"); assert parsed.value is None and parsed.status==ValueStatus.SUPPRESSED

def test_missing_is_distinct_from_suppressed():
    assert parse_published_count("").status==ValueStatus.MISSING
    assert parse_published_count(float("nan")).status==ValueStatus.MISSING

def test_not_applicable_is_distinct(): assert parse_published_count("N/A").status==ValueStatus.NOT_APPLICABLE

def test_numeric_text_with_commas():
    parsed=parse_published_count("1,235"); assert parsed.value==1235 and parsed.status==ValueStatus.OBSERVED

def test_suppressed_value_not_eligible_for_precise_calculation():
    assert not eligible_for_precise_calculation(parse_published_count("*"),parse_published_count(100))
