#!/usr/bin/env python3
"""Project pipeline CLI.

The download stage requires internet access to official NHS/ONS sources. The
warehouse stage requires DuckDB. Failures stop the build rather than allowing
stale/fabricated outputs to pass silently.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from nhs_elective_intelligence.ingestion.rtt import download_rtt_history
from nhs_elective_intelligence.ingestion.wlmds import download_wlmds_history
from nhs_elective_intelligence.ingestion.kh03 import download_latest_timeseries
from nhs_elective_intelligence.ingestion.ods import download_nhs_trust_reference
from nhs_elective_intelligence.pipeline import (
    initialise_warehouse, load_config, load_rtt_facts_from_raw, project_paths
)

ROOT = Path(__file__).resolve().parents[1]


def download() -> None:
    project, sources = load_config(ROOT)
    paths = project_paths(ROOT)
    src = sources["sources"]
    logging.info("Discovering/downloading multi-year RTT history...")
    start_year = int(project["analysis"].get("rtt_history_start_fiscal_year", 2021))
    rtt_files = download_rtt_history(src["rtt"]["landing_page"], paths.raw, min_start_year=start_year)
    logging.info("RTT archives cached: %s", len(rtt_files))
    logging.info("Discovering/downloading available WLMDS history...")
    wlmds_files = download_wlmds_history(
        src["wlmds"]["landing_page"], paths.raw,
        src["wlmds"].get("summary_archive"), src["wlmds"].get("demographics_archive")
    )
    logging.info("WLMDS files cached: %s", len(wlmds_files))
    logging.info("Discovering/downloading KH03...")
    download_latest_timeseries(src["kh03"]["landing_page"], paths.raw)
    logging.info("Downloading current ODS NHS-trust reference report...")
    download_nhs_trust_reference(src["ods"]["trust_predefined_report"], paths.raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["download", "warehouse", "rtt", "all"], default="all")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if args.stage in {"download", "all"}:
        download()
    if args.stage in {"warehouse", "rtt", "all"}:
        path = initialise_warehouse(ROOT)
        logging.info("Warehouse initialised: %s", path)
    if args.stage in {"rtt", "all"}:
        counts = load_rtt_facts_from_raw(ROOT)
        logging.info("RTT facts loaded: %s", counts)
    if args.stage == "all":
        logging.info("Download, warehouse initialisation and RTT core transformation complete; run documented WLMDS/KH03 adapters and validation exports next.")


if __name__ == "__main__":
    main()
