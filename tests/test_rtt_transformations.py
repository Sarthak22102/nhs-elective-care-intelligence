import pandas as pd
import pytest

from nhs_elective_intelligence.transformations.rtt import transform_rtt_full_csv


def _fixture():
    base={"Period":"RTT-Jul-26","Provider Org Code":"RXX","Provider Org Name":"Example NHS Trust","Commissioner Org Code":"01H"}
    rows=[]
    for tfc_code,tfc_name in [("C_100","General Surgery Service"),("TOTAL","Total")]:
        rows.extend([
            {**base,"Treatment Function Code":tfc_code,"Treatment Function Name":tfc_name,"RTT Part Type":"Part_2","Total All":100,"Gt 00 To 01 Weeks SUM 1":20,"Gt 17 To 18 Weeks SUM 1":30,"Gt 52 To 53 Weeks SUM 1":4,"Gt 65 To 66 Weeks SUM 1":3,"Gt 78 To 79 Weeks SUM 1":2,"Gt 104 Weeks SUM 1":1},
            {**base,"Treatment Function Code":tfc_code,"Treatment Function Name":tfc_name,"RTT Part Type":"Part_2A","Total All":9},
            {**base,"Treatment Function Code":tfc_code,"Treatment Function Name":tfc_name,"RTT Part Type":"Part_1A","Total All":25},
            {**base,"Treatment Function Code":tfc_code,"Treatment Function Name":tfc_name,"RTT Part Type":"Part_1B","Total All":35},
            {**base,"Treatment Function Code":tfc_code,"Treatment Function Name":tfc_name,"RTT Part Type":"Part_3","Total All":70},
        ])
    rows.append({**base,"Commissioner Org Code":"NONC","Treatment Function Code":"TOTAL","Treatment Function Name":"Total","RTT Part Type":"Part_2","Total All":999,"Gt 00 To 01 Weeks SUM 1":999})
    return pd.DataFrame(rows)


def test_rtt_total_and_specialty_grain_are_kept_separate():
    facts=transform_rtt_full_csv(_fixture())
    assert set(facts.waiting_list["treatment_function_code"])=={"C_100","TOTAL"}
    total=facts.waiting_list.query("treatment_function_code == 'TOTAL'").iloc[0]
    assert total["total_incomplete"]==100 and total["decision_to_admit_incomplete"]==9


def test_rtt_wait_bands_and_activity_are_derived_from_official_parts():
    facts=transform_rtt_full_csv(_fixture()); total=facts.waiting_list.query("treatment_function_code == 'TOTAL'").iloc[0]
    assert total["within_18_weeks"]==50
    assert total["over_52_weeks"]==10
    assert total["over_65_weeks"]==6
    assert total["over_78_weeks"]==3
    assert total["over_104_weeks"]==1
    flow=facts.activity.query("treatment_function_code == 'TOTAL'").iloc[0]
    assert flow["admitted_completed"]==25 and flow["non_admitted_completed"]==35 and flow["new_rtt_periods"]==70


def test_rtt_transform_fails_closed_on_unknown_schema():
    with pytest.raises(ValueError,match="missing required columns"):
        transform_rtt_full_csv(pd.DataFrame({"Period":["RTT-Jul-26"]}))
