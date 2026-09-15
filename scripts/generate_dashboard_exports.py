#!/usr/bin/env python3
"""Export dashboard-ready marts from DuckDB after a successful full refresh."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"data/processed/nhs_elective_care.duckdb"
OUT=ROOT/"data/processed/dashboard"
OUT.mkdir(parents=True,exist_ok=True)

try:
    import duckdb
except ImportError as exc:
    raise SystemExit("Install project dependencies first: pip install -e .") from exc

with duckdb.connect(str(DB), read_only=True) as con:
    exports={
        "provider_monthly":"SELECT * FROM mart_provider_monthly",
        "dim_provider":"SELECT * FROM dim_provider",
        "dim_date":"SELECT * FROM dim_date",
        "dim_specialty":"SELECT * FROM dim_specialty",
        "data_quality_results":"SELECT * FROM data_quality_results",
    }
    for name,sql in exports.items():
        target=(OUT/f"{name}.parquet").as_posix().replace("'","''")
        con.execute(f"COPY ({sql}) TO '{target}' (FORMAT PARQUET)")
        print(target)
