#!/usr/bin/env python3
"""Execute every analytical SQL question and export reviewable Parquet results."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/processed/nhs_elective_care.duckdb"
OUT = ROOT / "data/processed/analysis"

try:
    import duckdb
except ImportError as exc:
    raise SystemExit("Install project dependencies first: pip install -e .[dev]") from exc

if not DB.exists():
    raise SystemExit("Warehouse not found. Run: python scripts/run_pipeline.py --stage rtt")

OUT.mkdir(parents=True, exist_ok=True)
queries = sorted((ROOT / "sql").rglob("*.sql"))
if not queries:
    raise SystemExit("No analytical SQL files found.")

with duckdb.connect(str(DB), read_only=True) as con:
    for query_path in queries:
        relative = query_path.relative_to(ROOT / "sql")
        name = "__".join(relative.with_suffix("").parts)
        target = OUT / f"{name}.parquet"
        sql = query_path.read_text(encoding="utf-8")
        escaped = target.as_posix().replace("'", "''")
        con.execute(f"COPY ({sql}) TO '{escaped}' (FORMAT PARQUET)")
        print(f"{relative} -> {target.relative_to(ROOT)}")
