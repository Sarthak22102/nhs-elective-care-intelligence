# Reproduction guide

## 1. Create an environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -e .[dev]
```

Python 3.11+ is recommended.

## 2. Run verification tests before downloading data

```bash
pytest
```

The committed reference fixture can be regenerated with:

```bash
python scripts/build_verified_snapshot.py
```

## 3. Discover and download current official sources

```bash
python scripts/run_pipeline.py --stage download
```

RTT fiscal-year publication pages from 2021/22 onward and current/history attachments are discovered from official landing pages. Files are cached under `data/raw/` with metadata/checksums. If NHS changes a page/schema, the build should fail visibly rather than silently reinterpret columns.

## 4. Initialise DuckDB and load the core RTT facts

```bash
python scripts/run_pipeline.py --stage rtt
```

This creates `data/processed/nhs_elective_care.duckdb`, transforms the cached full RTT CSV archives, excludes `NONC`, separates published treatment-function totals from specialty detail, resolves explicit revisions, and loads the official waiting-list/activity facts. Use `--stage warehouse` only when you need an empty schema.

## 5. Run analytical SQL / validate additional-source adapters

```bash
python scripts/run_sql_analysis.py
```

The SQL runner writes each analysis result to `data/processed/analysis/`. WLMDS and KH03 ingestion adapters preserve their source-specific grain and suppression rules; do not enable a demographic/capacity finding until the relevant downloaded file schema has passed the validation checks documented in `reports/methodology.md`.

## 6. Dashboard

```bash
streamlit run app/streamlit_app.py
```

For Power BI, follow `dashboard/data_model.md`, `dashboard/dax_measures.md` and `dashboard/dashboard_specification.md`. No fake `.pbix` file is included.

## 7. Quality gate

Before publishing a refreshed analysis:

```bash
pytest
ruff check src tests scripts app
```

Then reconcile national/provider headline figures against the current NHS England RTT publication and inspect all error/warning rows in the data-quality table. Do not publish a pressure score, inequality rate or forecast until its required source fields pass these checks.
