"""NHS England Referral-to-Treatment (RTT) discovery and schema standardisation."""
from __future__ import annotations

import io
import logging
from pathlib import Path
import re
import zipfile

import pandas as pd

from nhs_elective_intelligence.cleaning.common import canonicalise_columns
from nhs_elective_intelligence.ingestion.http import discover_links, download_with_cache

LOGGER = logging.getLogger(__name__)

RTT_LINK_PATTERN = r"(Full[-_ ]CSV|full csv|provider.*csv|commissioner.*csv|\.zip|\.csv)"

ALIASES = {
    "provider_code": {"provider_org_code", "provider_code", "org_code", "organisation_code"},
    "provider_name": {"provider_org_name", "provider_name", "organisation_name"},
    "treatment_function_code": {"treatment_function_code", "treatment_function", "tfc"},
    "reporting_period": {"period", "reporting_period", "month", "data_period"},
}


def discover_rtt_publication_pages(main_page: str, min_start_year: int | None = None) -> list[str]:
    """Discover fiscal-year RTT publication pages, newest first."""
    links = discover_links(main_page, r"rtt-data-[0-9]{4}-[0-9]{2}|[0-9]{4}[-/][0-9]{2}.*RTT")
    scored: dict[int, str] = {}
    for url in links:
        match = re.search(r"rtt-data-(\d{4})-(\d{2})", url, re.I)
        if match:
            start = int(match.group(1))
            if min_start_year is None or start >= min_start_year:
                scored[start] = url
    if not scored:
        raise RuntimeError("Could not discover RTT fiscal-year publication pages.")
    return [scored[y] for y in sorted(scored, reverse=True)]


def discover_latest_rtt_publication_page(main_page: str) -> str:
    return discover_rtt_publication_pages(main_page)[0]


def discover_rtt_files(publication_page: str) -> list[str]:
    return discover_links(publication_page, RTT_LINK_PATTERN)


def _rename_known_aliases(df: pd.DataFrame) -> pd.DataFrame:
    work = canonicalise_columns(df)
    reverse: dict[str, str] = {}
    for canonical, aliases in ALIASES.items():
        for alias in aliases:
            if alias in work.columns:
                reverse[alias] = canonical
                break
    return work.rename(columns=reverse)


def read_rtt_csv(path_or_bytes: str | Path | bytes) -> pd.DataFrame:
    if isinstance(path_or_bytes, bytes):
        return _rename_known_aliases(pd.read_csv(io.BytesIO(path_or_bytes), low_memory=False))
    return _rename_known_aliases(pd.read_csv(path_or_bytes, low_memory=False))


def read_rtt_archive(path: str | Path) -> dict[str, pd.DataFrame]:
    """Read CSV members from an NHS RTT ZIP; member names are retained."""
    out: dict[str, pd.DataFrame] = {}
    with zipfile.ZipFile(path) as archive:
        for member in archive.namelist():
            if member.lower().endswith(".csv") and not member.endswith("/"):
                with archive.open(member) as handle:
                    out[member] = _rename_known_aliases(pd.read_csv(handle, low_memory=False))
    if not out:
        raise ValueError(f"No CSV members found in RTT archive {path}")
    return out


def download_latest_full_csv(publication_page: str, raw_dir: str | Path) -> Path:
    links = discover_rtt_files(publication_page)
    candidates = [u for u in links if re.search(r"full.*csv.*(?:zip|\.zip)", u, re.I)]
    if not candidates:
        candidates = [u for u in links if u.lower().endswith(".zip")]
    if not candidates:
        raise RuntimeError("No RTT full CSV ZIP discovered. Inspect the publication page/schema change.")
    path, _ = download_with_cache(candidates[0], Path(raw_dir) / "rtt")
    return path


def download_rtt_history(main_page: str, raw_dir: str | Path, min_start_year: int = 2021) -> list[Path]:
    """Download all discoverable monthly full-CSV archives from fiscal year onward."""
    pages = discover_rtt_publication_pages(main_page, min_start_year=min_start_year)
    urls: list[str] = []
    for page in pages:
        links = discover_rtt_files(page)
        full = [u for u in links if re.search(r"full.*csv.*(?:zip|\.zip)", u, re.I)]
        for url in full:
            if url not in urls:
                urls.append(url)
    if not urls:
        raise RuntimeError("No RTT full CSV archives discovered across requested history.")
    downloaded: list[Path] = []
    for url in urls:
        path, _ = download_with_cache(url, Path(raw_dir) / "rtt")
        downloaded.append(path)
    return downloaded
