"""NHS England KH03 bed availability/occupancy ingestion."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from nhs_elective_intelligence.cleaning.common import canonicalise_columns
from nhs_elective_intelligence.ingestion.http import discover_links, download_with_cache
from nhs_elective_intelligence.transformations.metrics import safe_divide


def discover_kh03_files(landing_page: str) -> list[str]:
    return discover_links(landing_page, r"(?:bed|Beds).*Timeseries.*(?:xlsx|xls|csv)")


def read_kh03(path: str | Path, sheet_name: int | str = 0) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return canonicalise_columns(pd.read_excel(path, sheet_name=sheet_name))
    return canonicalise_columns(pd.read_csv(path, low_memory=False))


def occupancy_rate(occupied_bed_days: float | None, available_bed_days: float | None) -> float | None:
    return safe_divide(occupied_bed_days, available_bed_days)


def download_latest_timeseries(landing_page: str, raw_dir: str | Path) -> Path:
    links = discover_kh03_files(landing_page)
    if not links:
        raise RuntimeError("No KH03 bed timeseries file discovered.")
    path, _ = download_with_cache(links[0], Path(raw_dir) / "kh03")
    return path
