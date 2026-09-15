"""Waiting List Minimum Data Set (WLMDS) management-information ingestion."""
from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

from nhs_elective_intelligence.cleaning.common import canonicalise_columns
from nhs_elective_intelligence.cleaning.suppression import parse_published_count
from nhs_elective_intelligence.ingestion.http import discover_links, download_with_cache


def discover_wlmds_files(landing_page: str) -> dict[str, list[str]]:
    return {
        "summary": discover_links(landing_page, r"WLMDS.*(?:xlsx|xls|csv)"),
        "demographics": discover_links(landing_page, r"(?:demograph|age|ethnicity|deprivation|sex).*(?:csv|xlsx|zip)"),
    }


def read_wlmds_table(path: str | Path, sheet_name: int | str = 0) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        frame = pd.read_excel(path, sheet_name=sheet_name)
    else:
        frame = pd.read_csv(path, low_memory=False)
    return canonicalise_columns(frame)


def parse_demographic_value_columns(df: pd.DataFrame, value_columns: list[str]) -> pd.DataFrame:
    """Add numeric/status columns for published demographic counts."""
    out = df.copy()
    for col in value_columns:
        parsed = out[col].map(parse_published_count)
        out[f"{col}_numeric"] = parsed.map(lambda p: p.value)
        out[f"{col}_status"] = parsed.map(lambda p: p.status.value)
    return out


def download_discovered_files(landing_page: str, raw_dir: str | Path) -> list[Path]:
    files = discover_wlmds_files(landing_page)
    urls = list(dict.fromkeys(files["summary"] + files["demographics"]))
    if not urls:
        raise RuntimeError("No WLMDS files discovered; publication layout may have changed.")
    downloaded: list[Path] = []
    for url in urls:
        path, _ = download_with_cache(url, Path(raw_dir) / "wlmds")
        downloaded.append(path)
    return downloaded


def discover_wlmds_history_files(
    landing_page: str,
    summary_archive: str | None = None,
    demographics_archive: str | None = None,
) -> list[str]:
    """Discover current plus historical WLMDS publication files."""
    pages = [landing_page] + [p for p in [summary_archive, demographics_archive] if p]
    urls: list[str] = []
    for page in pages:
        links = discover_links(page, r"WLMDS.*(?:csv|xlsx|xls|zip)|Demographics.*(?:csv|xlsx|xls|zip)")
        for url in links:
            if url not in urls:
                urls.append(url)
    return urls


def download_wlmds_history(
    landing_page: str,
    raw_dir: str | Path,
    summary_archive: str | None = None,
    demographics_archive: str | None = None,
) -> list[Path]:
    urls = discover_wlmds_history_files(landing_page, summary_archive, demographics_archive)
    if not urls:
        raise RuntimeError("No WLMDS current/archive files discovered.")
    downloaded: list[Path] = []
    for url in urls:
        path, _ = download_with_cache(url, Path(raw_dir) / "wlmds")
        downloaded.append(path)
    return downloaded
