"""Orchestration entry point for the reproducible warehouse build."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import json
import logging

import pandas as pd
import yaml

from nhs_elective_intelligence.ingestion.rtt import read_rtt_archive, read_rtt_csv
from nhs_elective_intelligence.transformations.rtt import RTTFacts, transform_rtt_full_csv

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    raw: Path
    interim: Path
    processed: Path
    warehouse: Path


def load_config(root: str | Path) -> tuple[dict, dict]:
    root = Path(root)
    project = yaml.safe_load((root / "config/project.yml").read_text(encoding="utf-8"))
    sources = yaml.safe_load((root / "config/sources.yml").read_text(encoding="utf-8"))
    return project, sources


def project_paths(root: str | Path) -> ProjectPaths:
    root = Path(root).resolve()
    project, _ = load_config(root)
    cfg = project["project"]
    return ProjectPaths(root=root, raw=root / cfg["raw_dir"], interim=root / cfg["interim_dir"], processed=root / cfg["processed_dir"], warehouse=root / cfg["warehouse"])


def require_duckdb():
    try:
        import duckdb  # type: ignore
    except ImportError as exc:
        raise RuntimeError("DuckDB is required for the warehouse stage. Install project dependencies with `pip install -e .`.") from exc
    return duckdb


def initialise_warehouse(root: str | Path) -> Path:
    paths = project_paths(root)
    paths.processed.mkdir(parents=True, exist_ok=True)
    duckdb = require_duckdb()
    schema_sql = (paths.root / "database/schema.sql").read_text(encoding="utf-8")
    with duckdb.connect(str(paths.warehouse)) as con:
        con.execute(schema_sql)
    return paths.warehouse


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_metadata(path: Path) -> dict:
    meta = path.parent / "_metadata" / f"{path.name}.json"
    if meta.exists():
        return json.loads(meta.read_text(encoding="utf-8"))
    return {"url": None, "sha256": _file_sha256(path), "downloaded_at_utc": None}


def _transform_rtt_source(path: Path) -> RTTFacts:
    if path.suffix.lower() == ".zip":
        members = read_rtt_archive(path)
        transformed: list[RTTFacts] = []
        errors: list[str] = []
        for name, frame in members.items():
            try:
                transformed.append(transform_rtt_full_csv(frame))
            except ValueError as exc:
                errors.append(f"{name}: {exc}")
        if not transformed:
            raise RuntimeError(f"No valid RTT full-CSV member in {path.name}: {'; '.join(errors)}")
        if len(transformed) > 1:
            raise RuntimeError(f"Ambiguous RTT archive {path.name}: {len(transformed)} members match the full schema. Inspect the upstream schema before loading.")
        return transformed[0]
    if path.suffix.lower() == ".csv":
        return transform_rtt_full_csv(read_rtt_csv(path))
    raise ValueError(f"Unsupported RTT source type: {path}")


def _select_rtt_revisions(candidates: list[tuple[Path, RTTFacts]]) -> list[tuple[Path, RTTFacts]]:
    by_month: dict[pd.Timestamp, list[tuple[Path, RTTFacts]]] = {}
    for path, facts in candidates:
        months = pd.Index(facts.waiting_list["reporting_month"].dropna().unique())
        if len(months) != 1:
            raise RuntimeError(f"Expected one RTT reporting month per archive, got {len(months)} in {path.name}")
        by_month.setdefault(pd.Timestamp(months[0]), []).append((path, facts))
    selected: list[tuple[Path, RTTFacts]] = []
    for month, items in sorted(by_month.items()):
        if len(items) == 1:
            selected.append(items[0]); continue
        explicit = [item for item in items if any(token in item[0].name.lower() for token in ("revis", "rev", "v2", "v3"))]
        if len(explicit) == 1:
            LOGGER.warning("Using explicitly revised RTT source for %s: %s", month.date(), explicit[0][0].name)
            selected.append(explicit[0]); continue
        names = ", ".join(item[0].name for item in items)
        raise RuntimeError(f"Multiple RTT sources found for {month.date()} without an unambiguous revised file: {names}. Resolve the revision explicitly rather than double-counting or guessing.")
    return selected


def load_rtt_facts_from_raw(root: str | Path) -> dict[str, int]:
    paths = project_paths(root)
    source_dir = paths.raw / "rtt"
    files = sorted([*source_dir.glob("*.zip"), *source_dir.glob("*.csv")])
    if not files:
        raise RuntimeError(f"No RTT archives found in {source_dir}; run the download stage first.")
    selected = _select_rtt_revisions([(path, _transform_rtt_source(path)) for path in files])
    waiting_frames: list[pd.DataFrame] = []
    activity_frames: list[pd.DataFrame] = []
    specialty_frames: list[pd.DataFrame] = []
    registry_rows: list[dict] = []
    extracted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    for path, facts in selected:
        meta = _download_metadata(path); source_name = str(path.relative_to(paths.root)); checksum = meta.get("sha256") or _file_sha256(path)
        waiting = facts.waiting_list.copy(); waiting["estimated_or_submitted"] = None; waiting["source_file"] = source_name; waiting["source_sha256"] = checksum; waiting["extraction_timestamp"] = extracted_at; waiting_frames.append(waiting)
        activity = facts.activity.copy(); activity["source_file"] = source_name; activity["source_sha256"] = checksum; activity["extraction_timestamp"] = extracted_at; activity_frames.append(activity)
        specialties = facts.specialties.copy(); specialties["source_url"] = meta.get("url"); specialty_frames.append(specialties)
        month = pd.Timestamp(waiting["reporting_month"].iloc[0]).strftime("%Y-%m")
        registry_rows.append({"dataset_name":"Consultant-led Referral to Treatment (RTT) full CSV","source_url":meta.get("url") or f"local:{source_name}","publisher":"NHS England","classification":"Accredited Official Statistics","publication_period":month,"extraction_timestamp":extracted_at,"source_sha256":checksum,"revision_note":"Explicit revised source selected where filename identified a revision; ambiguous duplicates fail the build."})
    waiting_all = pd.concat(waiting_frames, ignore_index=True); activity_all = pd.concat(activity_frames, ignore_index=True)
    specialties_all = pd.concat(specialty_frames, ignore_index=True).drop_duplicates(["treatment_function_code","treatment_function_name","is_total"])
    if waiting_all[["provider_code","treatment_function_code"]].isna().any().any(): raise RuntimeError("RTT transformed facts contain missing provider or treatment-function codes.")
    if activity_all[["provider_code","treatment_function_code"]].isna().any().any(): raise RuntimeError("RTT transformed activity contains missing provider or treatment-function codes.")
    duckdb = require_duckdb()
    with duckdb.connect(str(paths.warehouse)) as con:
        con.execute((paths.root / "database/schema.sql").read_text(encoding="utf-8"))
        con.execute("DELETE FROM fact_rtt_waiting_list"); con.execute("DELETE FROM fact_rtt_activity"); con.execute("DELETE FROM dim_specialty"); con.execute("DELETE FROM source_registry WHERE dataset_name = 'Consultant-led Referral to Treatment (RTT) full CSV'")
        con.register("waiting_df", waiting_all); con.execute("""INSERT INTO fact_rtt_waiting_list SELECT reporting_month, provider_code, treatment_function_code, total_incomplete, within_18_weeks, over_52_weeks, over_65_weeks, over_78_weeks, over_104_weeks, decision_to_admit_incomplete, estimated_or_submitted, source_file, source_sha256, extraction_timestamp FROM waiting_df"""); con.unregister("waiting_df")
        con.register("activity_df", activity_all); con.execute("""INSERT INTO fact_rtt_activity SELECT reporting_month, provider_code, treatment_function_code, new_rtt_periods, admitted_completed, non_admitted_completed, source_file, source_sha256, extraction_timestamp FROM activity_df"""); con.unregister("activity_df")
        specialty_dim = specialties_all.sort_values(["treatment_function_code","treatment_function_name"]).drop_duplicates("treatment_function_code", keep="last")
        con.register("specialty_df", specialty_dim); con.execute("""INSERT INTO dim_specialty (treatment_function_code, treatment_function_name, specialty_group, is_total, source_url) SELECT treatment_function_code, treatment_function_name, NULL, is_total, source_url FROM specialty_df WHERE treatment_function_code IS NOT NULL"""); con.unregister("specialty_df")
        registry = pd.DataFrame(registry_rows); con.register("registry_df", registry); con.execute("INSERT INTO source_registry SELECT * FROM registry_df"); con.unregister("registry_df")
    return {"rtt_source_files":len(selected),"waiting_list_rows":len(waiting_all),"activity_rows":len(activity_all),"specialty_rows":len(specialty_dim)}
