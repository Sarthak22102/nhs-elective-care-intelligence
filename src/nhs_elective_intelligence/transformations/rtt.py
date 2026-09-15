"""Transform NHS England monthly RTT full-CSV extracts into analytical facts.

The official full CSV contains both treatment-function detail and ``Total`` rows.
This module preserves that distinction explicitly so provider-level totals are not
obtained by summing detail plus total rows.
"""
from __future__ import annotations

import re
from datetime import datetime
from dataclasses import dataclass

import numpy as np
import pandas as pd

from nhs_elective_intelligence.cleaning.common import canonicalise_columns

PART_ALIASES = {"part_1a":"admitted_completed","part_1b":"non_admitted_completed","part_2":"incomplete","part_2a":"decision_to_admit_incomplete","part_3":"new_rtt_periods"}
REQUIRED_BASE_COLUMNS = {"period","provider_org_code","commissioner_org_code","treatment_function_name","rtt_part_type","total_all"}

@dataclass(frozen=True)
class RTTFacts:
    waiting_list: pd.DataFrame
    activity: pd.DataFrame
    specialties: pd.DataFrame


def _parse_period(value: object) -> pd.Timestamp:
    if pd.isna(value): return pd.NaT
    text = re.sub(r"^RTT[-_ ]*", "", str(value).strip(), flags=re.I)
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=False)
    if pd.isna(parsed):
        for fmt in ("%b-%y","%b-%Y","%B-%y","%B-%Y","%Y-%m"):
            try:
                parsed = pd.Timestamp(datetime.strptime(text, fmt)); break
            except (ValueError, TypeError):
                continue
    return pd.NaT if pd.isna(parsed) else pd.Timestamp(parsed) + pd.offsets.MonthEnd(0)


def _normalise_part(value: object) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
    return text.replace("part_1_a","part_1a").replace("part_1_b","part_1b").replace("part_2_a","part_2a")


def _wait_band_lower_week(column: str) -> int | None:
    match = re.search(r"(?:^|_)gt_(\d{1,3})_to_(\d{1,3})_weeks", column)
    if match: return int(match.group(1))
    match = re.search(r"(?:^|_)gt_(\d{1,3})_weeks", column)
    return int(match.group(1)) if match else None


def _numeric_sum(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    if not columns: return pd.Series(np.nan, index=df.index, dtype="float64")
    return df[columns].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)


def _standardise_rtt_frame(df: pd.DataFrame) -> pd.DataFrame:
    work = canonicalise_columns(df).copy()
    aliases = {"reporting_period":"period","provider_code":"provider_org_code","provider_name":"provider_org_name","treatment_function_code":"treatment_function_code"}
    work = work.rename(columns={k:v for k,v in aliases.items() if k in work.columns and v not in work.columns})
    missing = sorted(REQUIRED_BASE_COLUMNS - set(work.columns))
    if missing: raise ValueError(f"RTT extract is missing required columns: {missing}")
    if "treatment_function_code" not in work.columns: work["treatment_function_code"] = pd.NA
    if "provider_org_name" not in work.columns: work["provider_org_name"] = pd.NA
    work["reporting_month"] = work["period"].map(_parse_period)
    if work["reporting_month"].isna().any():
        bad = work.loc[work["reporting_month"].isna(),"period"].drop_duplicates().head(5).tolist(); raise ValueError(f"Unparseable RTT reporting periods: {bad}")
    work["provider_org_code"] = work["provider_org_code"].astype("string").str.strip().str.upper()
    work["commissioner_org_code"] = work["commissioner_org_code"].astype("string").str.strip().str.upper()
    work["rtt_part"] = work["rtt_part_type"].map(_normalise_part)
    is_total = work["treatment_function_name"].astype("string").str.strip().str.casefold().eq("total")
    tfc = work["treatment_function_code"].astype("string").str.strip()
    work["treatment_function_code"] = tfc.where(~is_total, "TOTAL")
    work.loc[~is_total & work["treatment_function_code"].isin(["","<NA>"]),"treatment_function_code"] = pd.NA
    work["is_total_specialty"] = is_total
    work["total_all"] = pd.to_numeric(work["total_all"], errors="coerce")
    return work.loc[work["commissioner_org_code"].ne("NONC")].copy()


def transform_rtt_full_csv(df: pd.DataFrame) -> RTTFacts:
    work = _standardise_rtt_frame(df)
    band_columns = {c:lower for c in work.columns if (lower := _wait_band_lower_week(c)) is not None}
    incomplete = work.loc[work["rtt_part"].eq("part_2")].copy()
    if incomplete.empty: raise ValueError("RTT extract contains no Part_2 incomplete-pathway rows.")
    incomplete["within_18_weeks"] = _numeric_sum(incomplete,[c for c,l in band_columns.items() if l < 18])
    incomplete["over_52_weeks"] = _numeric_sum(incomplete,[c for c,l in band_columns.items() if l >= 52])
    incomplete["over_65_weeks"] = _numeric_sum(incomplete,[c for c,l in band_columns.items() if l >= 65])
    incomplete["over_78_weeks"] = _numeric_sum(incomplete,[c for c,l in band_columns.items() if l >= 78])
    incomplete["over_104_weeks"] = _numeric_sum(incomplete,[c for c,l in band_columns.items() if l >= 104])
    keys = ["reporting_month","provider_org_code","treatment_function_code"]
    waiting = incomplete.groupby(keys,dropna=False,as_index=False).agg(total_incomplete=("total_all","sum"),within_18_weeks=("within_18_weeks","sum"),over_52_weeks=("over_52_weeks","sum"),over_65_weeks=("over_65_weeks","sum"),over_78_weeks=("over_78_weeks","sum"),over_104_weeks=("over_104_weeks","sum")).rename(columns={"provider_org_code":"provider_code"})
    dta = work.loc[work["rtt_part"].eq("part_2a")]
    if not dta.empty:
        dta_agg = dta.groupby(keys,dropna=False,as_index=False)["total_all"].sum().rename(columns={"provider_org_code":"provider_code","total_all":"decision_to_admit_incomplete"})
        waiting = waiting.merge(dta_agg,on=["reporting_month","provider_code","treatment_function_code"],how="left",validate="one_to_one")
    else: waiting["decision_to_admit_incomplete"] = np.nan
    flows=[]
    for part,measure in PART_ALIASES.items():
        if measure in {"incomplete","decision_to_admit_incomplete"}: continue
        subset=work.loc[work["rtt_part"].eq(part)]
        if subset.empty: continue
        flows.append(subset.groupby(keys,dropna=False,as_index=False)["total_all"].sum().rename(columns={"provider_org_code":"provider_code","total_all":measure}))
    if flows:
        activity=flows[0]; join_keys=["reporting_month","provider_code","treatment_function_code"]
        for flow in flows[1:]: activity=activity.merge(flow,on=join_keys,how="outer",validate="one_to_one")
    else: activity=pd.DataFrame(columns=["reporting_month","provider_code","treatment_function_code","new_rtt_periods","admitted_completed","non_admitted_completed"])
    for measure in ("new_rtt_periods","admitted_completed","non_admitted_completed"):
        if measure not in activity.columns: activity[measure]=np.nan
    specialties=work[["treatment_function_code","treatment_function_name","is_total_specialty"]].drop_duplicates().rename(columns={"is_total_specialty":"is_total"})
    if specialties["treatment_function_code"].duplicated().any():
        conflicts=specialties.loc[specialties["treatment_function_code"].duplicated(False),"treatment_function_code"].dropna().unique()
        if len(conflicts): raise ValueError(f"Conflicting treatment-function labels for codes: {conflicts[:5].tolist()}")
    return RTTFacts(waiting.sort_values(["reporting_month","provider_code","treatment_function_code"]).reset_index(drop=True),activity.sort_values(["reporting_month","provider_code","treatment_function_code"]).reset_index(drop=True),specialties.sort_values("treatment_function_code",na_position="last").reset_index(drop=True))
