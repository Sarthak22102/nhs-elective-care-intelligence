# Security and governance review

## Scope

Public aggregate NHS/ONS data only. This repository is a service-level analytical portfolio project, not a clinical decision system and not a patient-level risk model.

## Controls

- No passwords, API keys, tokens or private credentials are required for source downloads.
- `.env*`, raw data, local databases, PBIX files, caches and logs are excluded from version control.
- No patient-identifiable data are ingested or generated.
- Suppressed WLMDS cells are not reconstructed or combined to defeat disclosure controls.
- Source URLs and checksums are retained for provenance; local absolute filesystem paths are not written into committed configuration.
- Download helper uses bounded retries, explicit timeout, atomic `.part` writes and content provenance.
- Large raw NHS files are downloaded locally rather than committed to GitHub.
- Dependency ranges are pinned to major versions; CI installs a clean environment and runs tests/lint.

## Build scan

A final local scan checks likely secret patterns, oversized files, absolute local paths, compiled caches and test status. Findings are recorded in the final build summary.

## Pre-publication dependency hardening (2026-09-15)

Before GitHub publication, the dependency floors and downloader were hardened against reviewed advisories:

- `requests>=2.32.4` to exclude CVE-2024-47081 affected releases; public-data sessions also set `trust_env=False` so `.netrc` and proxy credentials are not inherited.
- `streamlit>=1.54` to exclude the Windows SSRF / NTLM credential-exposure issue fixed in 1.54.0.
- `setuptools>=70` to exclude CVE-2024-6345 affected build-tool releases.
- `duckdb>=1.4.2` to exclude the DuckDB 1.4.0–1.4.1 encryption implementation advisory, even though this project does not enable database encryption.
- Removed unused `scipy`, `statsmodels`, and `scikit-learn` runtime dependencies to reduce dependency and supply-chain surface.
- CI upgrades to `pip>=26.2` before installation and runs `pip-audit` on every push/PR.
- The HTTP ingestion helper now permits HTTPS only and allow-lists the authoritative NHS England, NHS Digital/ODS, ONS and GOV.UK hosts used by this project.

These controls reduce known package and source-fetching risk; they do not guarantee absence of future vulnerabilities. GitHub/Dependabot or equivalent continuous dependency monitoring should remain enabled for the public repository.
