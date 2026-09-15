"""Organisation Data Service (ODS) reference-data helpers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd

from nhs_elective_intelligence.cleaning.common import canonicalise_columns, normalise_code
from nhs_elective_intelligence.ingestion.http import download_with_cache


@dataclass(frozen=True)
class ProviderResolution:
    provider_code: str
    provider_name: str | None
    status: str | None
    successor_code: str | None = None


def read_ods_csv(path: str | Path) -> pd.DataFrame:
    df = canonicalise_columns(pd.read_csv(path, low_memory=False))
    for candidate in ["organisation_code", "org_code", "code"]:
        if candidate in df.columns:
            df["provider_code"] = df[candidate].map(normalise_code)
            break
    if "provider_code" not in df.columns:
        raise ValueError("Could not identify an ODS organisation-code column.")
    return df


def build_code_set(ods: pd.DataFrame) -> set[str]:
    return set(ods["provider_code"].dropna().astype(str).str.upper())


def download_nhs_trust_reference(report_url: str, raw_dir: str | Path) -> Path:
    """Download ODS DSE `etr` NHS-trust predefined report.

    ODS DSE reports are dynamic and refresh nightly, so download metadata and
    checksum provide the build-time reference snapshot used for provider validation.
    """
    path, _ = download_with_cache(report_url, Path(raw_dir) / "ods")
    return path
