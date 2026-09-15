import pandas as pd

from nhs_elective_intelligence.validation.checks import duplicate_key_check, extreme_mom_flags, non_negative_check, provider_code_validity, required_null_check


def test_duplicate_key_detected():
    df=pd.DataFrame({"month":["2026-01","2026-01"],"provider":["A","A"]}); result=duplicate_key_check(df,["month","provider"])
    assert not result.passed and result.failed_rows==2

def test_required_null_detected():
    result=required_null_check(pd.DataFrame({"provider":["A",None]}),["provider"]); assert result.failed_rows==1

def test_negative_counts_detected():
    result=non_negative_check(pd.DataFrame({"count":[3,-1,0]}),["count"]); assert result.failed_rows==1

def test_extreme_change_is_flagged_not_deleted():
    df=pd.DataFrame({"provider":["A","A","A"],"month":pd.to_datetime(["2026-01-31","2026-02-28","2026-03-31"]),"backlog":[100,110,180]})
    flags=extreme_mom_flags(df,"backlog",["provider"],"month",0.30)
    assert len(flags)==1 and flags.iloc[0]["backlog"]==180 and len(df)==3

def test_provider_code_validity_warns_unknown_code():
    result=provider_code_validity(pd.DataFrame({"provider_code":["AAA","BAD"]}),"provider_code",{"AAA","BBB"})
    assert not result.passed and "BAD" in result.detail
