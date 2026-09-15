"""Data-quality checks that flag rather than silently delete observations."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class CheckResult:
    check: str
    passed: bool
    failed_rows: int
    severity: str
    detail: str

def duplicate_key_check(df: pd.DataFrame, keys: list[str], severity: str = "error") -> CheckResult:
    missing=[k for k in keys if k not in df.columns]
    if missing: return CheckResult("duplicate_primary_key",False,len(df),"error",f"Missing key columns: {missing}")
    mask=df.duplicated(keys,keep=False); n=int(mask.sum()); return CheckResult("duplicate_primary_key",n==0,n,severity,f"keys={keys}")

def required_null_check(df: pd.DataFrame, columns: list[str], severity: str = "error") -> CheckResult:
    missing_cols=[c for c in columns if c not in df.columns]
    if missing_cols: return CheckResult("required_nulls",False,len(df),"error",f"Missing columns: {missing_cols}")
    n=int(df[columns].isna().any(axis=1).sum()); return CheckResult("required_nulls",n==0,n,severity,f"columns={columns}")

def non_negative_check(df: pd.DataFrame, columns: list[str], severity: str = "error") -> CheckResult:
    present=[c for c in columns if c in df.columns]
    if not present: return CheckResult("negative_counts",False,len(df),"error","No requested numeric columns found")
    n=int((df[present].apply(pd.to_numeric,errors="coerce")<0).any(axis=1).sum()); return CheckResult("negative_counts",n==0,n,severity,f"columns={present}")

def extreme_mom_flags(df: pd.DataFrame,value_col: str,group_cols: list[str],date_col: str,absolute_pct_threshold: float=0.30) -> pd.DataFrame:
    work=df.copy().sort_values(group_cols+[date_col]); work["_previous"]=work.groupby(group_cols,dropna=False)[value_col].shift(1); denom=work["_previous"].where(work["_previous"]!=0); work["mom_pct_change"]=(work[value_col]-work["_previous"])/denom; return work[work["mom_pct_change"].abs()>absolute_pct_threshold].copy()

def provider_code_validity(df: pd.DataFrame, provider_col: str, valid_codes: set[str]) -> CheckResult:
    values=set(df[provider_col].dropna().astype(str).str.upper()); invalid=values-{c.upper() for c in valid_codes}; return CheckResult("provider_code_validity",not invalid,len(invalid),"warning" if invalid else "info",f"invalid_codes={sorted(invalid)}")
