# Data directory

Large NHS source files are intentionally not committed. The reproducible pipeline discovers and downloads them into `data/raw/`, records URL/checksum/HTTP metadata, then writes cleaned intermediates and analytical outputs locally.

## Committed reference extracts

`data/reference/official_gateway_elective_timeseries.csv` contains 48 verified records (England plus three provider benchmarks, Aug 2025-Jul 2026) transcribed from NHS England Public Data Gateway tables on 15 September 2026. `official_gateway_selected_provider_snapshot.csv` contains 14 selected July 2026 benchmark-provider rows from the same official gateway. These small extracts exist to make CI tests, documentation and dashboard prototypes reproducible when NHS binary publication attachments are unavailable in a restricted runtime.

They are **not** a substitute for the bulk RTT/WLMDS/KH03 pipeline and must not be presented as a complete provider dataset.

## Privacy

Only publicly published aggregate data are used. No patient-identifiable, confidential, record-level clinical or intentionally suppressed information is stored here.
