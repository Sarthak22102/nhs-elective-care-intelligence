import pandas as pd

from nhs_elective_intelligence.cleaning.common import canonical_column, canonicalise_columns, parse_reporting_month, normalise_code


def test_column_canonicalisation():
    assert canonical_column("Provider Org Code") == "provider_org_code"
    df = canonicalise_columns(pd.DataFrame({"Wait > 52 Weeks":[1]}))
    assert "wait_52_weeks" in df.columns


def test_report_date_becomes_month_end():
    assert parse_reporting_month("2026-07-01") == pd.Timestamp("2026-07-31")


def test_provider_code_normalised():
    assert normalise_code("  r1h ") == "R1H"
