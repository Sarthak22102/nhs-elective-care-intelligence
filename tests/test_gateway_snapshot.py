from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def _timeseries():
    return pd.read_csv(ROOT/"data/reference/official_gateway_elective_timeseries.csv")


def test_verified_snapshot_has_expected_grain_and_no_duplicates():
    df=_timeseries()
    assert len(df)==48
    assert not df.duplicated(["reporting_month","entity"]).any()


def test_verified_snapshot_covers_twelve_months():
    df=_timeseries()
    assert df["reporting_month"].nunique()==12
    assert df["entity"].nunique()==4


def test_july_2026_national_values_match_verified_gateway():
    df=_timeseries()
    row=df[(df.reporting_month=="2026-07-31") & (df.entity_type=="national")].iloc[0]
    assert row.within_18_weeks_pct==65.4
    assert row.over_52_weeks_pct==1.5


def test_mid_and_south_essex_july_values_match_verified_gateway():
    df=_timeseries()
    row=df[(df.reporting_month=="2026-07-31") & (df.entity.str.contains("Mid And South Essex"))].iloc[0]
    assert row.within_18_weeks_pct==49.8
    assert row.over_52_weeks_pct==7.9
