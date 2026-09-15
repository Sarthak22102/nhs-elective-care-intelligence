# Portfolio materials

## Three CV bullets — X / Y / Z

- **Built** a reproducible NHS elective-care intelligence platform with a 14-table DuckDB analytical design, **8 advanced SQL analyses and 44/44 passing automated tests**, using Python, pandas, SQL window functions, provenance-aware ingestion and suppression-safe data-quality controls.
- **Benchmarked** 12 months of official NHS England elective performance and quantified a **+4.4pp rise in England’s within-18-week share (61.0%→65.4%) alongside a -1.1pp fall in >52-week waits (2.6%→1.5%)**, using verified time-series comparisons and provider benchmark analysis.
- **Engineered** a responsible inequality/capacity framework across **5 authoritative source families and 4 explicit demographic value states**, using RTT/WLMDS source separation, disclosure-control-aware parsing, ODS organisation mapping and KH03 bed-capacity proxy rules without imputing suppressed counts.

> These bullets describe the analytical build/evidence only. They do not claim the project changed NHS operational performance.

## LinkedIn project description

**NHS Elective Care Intelligence – Waiting List, Capacity & Health Inequality Analytics**

Built a reproducible analytics platform for public NHS England elective-care data using Python, DuckDB, advanced SQL and Power BI modelling. The project separates RTT Accredited Official Statistics from WLMDS management information, adds provider/specialty flow metrics, suppression-aware demographic analysis, ODS organisation handling and KH03 bed-capacity proxies, with 44 automated tests. A verified 12-month NHS England snapshot showed the national within-18-week proportion increasing from 61.0% to 65.4% between Aug 2025 and Jul 2026, while the over-52-week proportion fell from 2.6% to 1.5%. The repository includes a star schema, DAX library, eight-page dashboard specification, Streamlit interface, methodology, data-quality framework and explicit limitations/ethics controls.

## GitHub repository description

Reproducible NHS elective-care analytics: RTT/WLMDS/KH03/ODS ingestion, DuckDB + advanced SQL, suppression-safe inequality analysis, Power BI model and tested operational-pressure metrics.

## 60-second interview explanation

I built NHS Elective Care Intelligence to show that I can do more than build a dashboard. I designed a reproducible pipeline around NHS England’s official RTT statistics, WLMDS management information, KH03 bed data and ODS reference data. RTT remains the authority for headline waiting-list KPIs, while WLMDS is used carefully for extra detail and demographics. I modelled the data in a DuckDB star schema, created SQL for rolling demand and throughput, provider deterioration, specialty drivers and capacity proxies, and added 44 automated tests including disclosure-control handling. In the verified official snapshot, England’s within-18-week share improved from 61.0% to 65.4% over 12 months, while the >52-week share fell from 2.6% to 1.5%. I also deliberately withheld unsupported forecasts, inequality findings and pressure scores when the full source files were not executable, which is part of how I demonstrate analytical judgement and data governance.

## 3-minute technical interview explanation

The project starts with source governance. Monthly RTT is Accredited Official Statistics, so I use it for headline incomplete pathways, completions, new RTT periods and waiting-time measures. WLMDS gives richer weekly and demographic detail but NHS England classifies it as management information, so I keep it in separate facts and never reconcile it by pretending it is the same total. KH03 is quarterly and only captures bed availability/occupancy, so I label derived measures as capacity proxies rather than “true capacity.” ODS is the organisation dimension because provider codes, mergers and successors matter over time.

The ingestion layer discovers current publication links, downloads with caching, logs source URLs/extraction timestamps/checksums and fails on unknown schema instead of guessing. Cleaning canonicalises fields and handles disclosure control explicitly: every demographic count has a value status such as observed, suppressed, missing or not applicable. A suppressed cell stays null and is not eligible for precise ratios or ranks.

The DuckDB model separates waiting-list stock, RTT activity, WLMDS pathways/demographics and bed capacity. The SQL layer uses CTEs and window functions for MoM/YoY change, rolling demand/throughput, consecutive deterioration, percentile benchmarking, rank movement and specialty backlog contribution. Demand is new RTT periods and throughput is admitted plus non-admitted completions at a compatible grain, but I also document NHS England’s “unreported removals” data-quality issue, so I do not claim new starts minus completions perfectly explains backlog change.

I implemented an explainable pressure-score function, but the build refuses to publish it unless enough validated components are present. The same principle applies to forecasting: the executed 12-month verification series fails a 24-month readiness gate, so no model is published merely to make the project look more advanced.

For BI delivery I created the Power BI star-schema specification, DAX library and eight-page report design, plus a Streamlit interface and data-backed mockups. In the executed official snapshot, national 18-week performance rose 4.4 percentage points and >52-week waits fell 1.1 points between Aug 2025 and Jul 2026. Mid And South Essex remained materially below the national 18-week benchmark and above the national >52-week proportion in July, which I frame as a priority for deeper investigation rather than a judgement about causes or quality of care.

## “Why did you build this project?”

I wanted a portfolio project that mirrors the real analytical challenges in UK healthcare: messy publication formats, changing organisations, different statistical statuses, stock-and-flow interpretation, disclosure control and the need to turn data into prioritised questions without overstating what the data can prove. It demonstrates analytics engineering, BI, statistical judgement and governance in one coherent system.

## “What was the hardest part?”

The hardest part was not a chart or algorithm; it was preserving comparability across sources. RTT, WLMDS and KH03 have different grains, classifications and limitations. I solved that by giving them separate fact tables, using RTT as the headline authority, refusing a speculative RTT-to-KH03 specialty mapping and making source/status metadata part of the model rather than footnotes.

## “How did you ensure data quality?”

I combined source provenance with automated tests and reconciliation rules. Downloads retain URL, extraction timestamp and SHA-256; tests cover duplicates, required identifiers, negative counts, ratio denominators, rolling metrics, provider-code validity, suppression parsing and forecast/pressure-score gates. Extreme changes are flagged for investigation instead of automatically deleted, and a full refresh requires reconciliation to official NHS headline values before findings are published.

## “How did you analyse inequality responsibly?”

I treated WLMDS demographic data as management information and preserved NHS disclosure controls. Suppressed cells are not zero, are not imputed and are not reverse-engineered. I distinguish waiting-list composition from population rates, and I only use ONS denominators when numerator and denominator geography/population are genuinely compatible. Provider-level associations are not presented as evidence of discrimination or individual treatment effects.

## “How did you measure capacity?”

I did not claim to measure total elective capacity. KH03 publishes available bed days by sector and occupied bed days by consultant main specialty, so I keep those grains separate and only form bed occupancy and activity-per-available-bed-day at provider/quarter level as operational/capacity proxies. I explicitly note that theatres, workforce, diagnostics, outpatient slots and case mix are missing, and I do not force a specialty mapping between KH03 and RTT.

## “Why did you choose these KPIs?”

I wanted to combine stock, timeliness and flow. Backlog size alone cannot tell whether performance is improving; the 18-week and long-wait rates add timeliness, while new RTT periods versus completed pathways adds flow. Rolling measures reduce single-month noise, and backlog per completion gives an interpretable scenario ratio. Every KPI has a defined source and denominator and is withheld if the source fields are not compatible.

## “What would you improve with access to internal NHS data?”

I would add validated patient-level or pathway-level operational data under the correct governance controls, richer theatre/workforce/diagnostic capacity measures, referral and cancellation reasons, case-mix/risk adjustment, provider-defined catchment denominators and operational event data. That would allow more defensible pathway-flow decomposition and intervention evaluation. I would still keep patient-identifiable data out of a public portfolio and separate descriptive/causal questions carefully.
