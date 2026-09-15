# Methodology

## Analytical question

The platform is designed to move from published waiting-list statistics to operational screening: where pressure is greatest, what is driving it, whether flow is keeping pace with demand, where long waits are concentrated, and which provider/specialty combinations merit investigation.

## Source hierarchy

1. Monthly RTT Accredited Official Statistics are authoritative for headline waiting-list and RTT activity KPIs.
2. WLMDS management information adds weekly/demographic detail but is never silently substituted for RTT national totals.
3. KH03 contributes a bed-availability/occupancy proxy, not a complete measure of elective clinical capacity.
4. ODS provides time-aware organisation reference data.
5. ONS denominators are used only after geography/population compatibility is demonstrated.

## Data engineering

Publication pages are discovered programmatically. Downloads are cached and accompanied by URL, UTC extraction timestamp, SHA-256, byte size, ETag and Last-Modified metadata where available. Schema adapters canonicalise column names conservatively: an unfamiliar schema is a build failure/quality issue, not an invitation to guess mappings.

The DuckDB warehouse separates waiting-list stock, RTT flow/activity, WLMDS details/demographics and KH03 bed data. Provider and specialty dimensions are shared only where keys are genuinely compatible. KH03 consultant-main-specialty is not force-mapped to RTT treatment function.

## KPI definitions

- **Total incomplete pathways:** published RTT pathways still waiting at month end.
- **18-week performance:** incomplete pathways waiting no more than 18 weeks / total incomplete pathways where source fields support the calculation.
- **Long-wait rate:** pathways over a chosen published threshold / total incomplete pathways.
- **Completed pathways:** admitted completed + non-admitted completed pathways at a common reporting grain.
- **Demand:** new RTT periods.
- **Demand-to-throughput ratio:** new RTT periods / completed pathways. Above 1 indicates more recorded starts than completions at the measured grain; it is not proof of inadequate clinical capacity because unreported removals and recording timing can affect flow reconciliation.
- **Net pathway pressure:** new RTT periods - completed pathways; interpreted with the same caveat.
- **Backlog per monthly completion:** incomplete pathways / monthly completed pathways; a scenario ratio, not a forecast of how long a waiting list will actually take to clear.
- **Bed occupancy proxy:** occupied bed days / available bed days after the two KH03 series are aggregated separately to provider/quarter/bed-type grain. Availability is published by sector, whereas occupancy is broken down by consultant main specialty; no specialty-level availability ratio is inferred.

## Pressure score

The code supports an explainable 0-100 composite based on percentile-normalised components, with equal weighting by default and component contributions retained. It refuses to score when fewer than the configured minimum components are present. **No project finding currently uses this composite**, because the restricted execution environment did not ingest the full RTT flow/KH03 files required to defend it. This is preferable to publishing an arbitrary score from incomplete evidence.

## Inequality methodology

WLMDS demographic cells are classified as `observed`, `suppressed`, `missing` or `not_applicable`. Precise gaps/ratios use observed cells only. Suppressed values are not imputed, ranked or reverse-engineered. Without compatible population denominators, demographic results are described as **waiting-list composition**, not prevalence or treatment-rate inequality. No causal inference about discrimination is made from aggregate published data.

## Statistical analysis

The project implements rolling summaries, lagged MoM/YoY comparisons, provider percentiles/ranks, persistent deterioration streaks, outlier flags and transparent gap/ratio measures. Statistical tests are only appropriate after checking assumptions and practical significance. The executed 12-month verification snapshot is too short for robust forecasting, so forecast output is deliberately withheld by the readiness gate.

## Validation principles

Headline values should reconcile to NHS England official outputs; national/provider totals are compared where possible. Extreme changes are flagged rather than auto-deleted. Revisions are retained through source checksums/provenance. Important metrics are independently unit-tested in Python and specified again in SQL/DAX for cross-layer reconciliation after a full refresh.
