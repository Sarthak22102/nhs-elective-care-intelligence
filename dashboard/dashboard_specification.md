# Executive dashboard specification

No fake `.pbix` is included. This specification is sufficient to build a native Power BI report against the validated analytical exports.

## Global behaviour

- Default reporting period: latest validated month from the model, never hard-coded.
- Core slicers: reporting period, provider, region/ICB where valid, treatment function.
- Demographic slicers appear only on the inequality page.
- Use tooltips for definitions/source status and a visible “official statistics vs management information” badge.
- Drill-through target: Provider Detail.
- Bookmarks: Executive / Operational / Data Quality views.
- Cross-filtering should be intentional; disable interactions that create ambiguous comparisons.
- Accessibility: high contrast, descriptive titles, keyboard focus order, alt text, colour never the sole signal.

## Page 1 — Elective Care Executive Overview

**Question:** Is national elective pressure improving, and where should attention go first?

KPI cards: total incomplete pathways; 18-week performance; >52-week pathways/rate; MoM backlog change; new RTT pathways; completed pathways; demand-throughput ratio; count of providers meeting a transparent “high pressure” screening rule.

Visuals: waiting-list trend with 18-week benchmark; demand vs throughput line; long-wait trend; provider pressure matrix; top specialty contributors to backlog change; compact “What changed?” narrative generated from validated measures only.

## Page 2 — Provider Performance

**Question:** Which organisations are under sustained pressure or improving?

Visuals: provider table with backlog, MoM/YoY growth, long-wait rate, demand-throughput ratio, rank movement and DQ icon; scatterplot of backlog-per-completion vs long-wait rate sized by backlog; small multiples for trend; national/peer benchmark variance bars.

Drill-through: right-click provider → Page 7.

## Page 3 — Specialty Pressure

**Question:** Which treatment functions are driving national/provider backlog movement?

Visuals: ranked backlog-change bar; specialty share of total backlog; demand vs throughput by treatment function; long-wait heatmap (provider × specialty); rolling trend small multiples.

Do not mix KH03 consultant specialties onto this page unless a validated mapping is later documented.

## Page 4 — Capacity & Operational Pressure

**Question:** How do bed availability/occupancy and recorded throughput align at provider level?

Visuals: provider bed occupancy trend formed from separately aggregated KH03 availability/occupancy facts; completions per available bed-day (explicitly labelled proxy); backlog-per-completion; provider matrix combining occupancy and flow indicators; quarterly capacity table. RTT specialty filters do not interact with KH03 capacity-proxy visuals.

Banner: **“Bed metrics are capacity proxies, not total elective clinical capacity.”**

## Page 5 — Health Inequality

**Question:** What observable differences exist in published waiting-list composition and, where compatible, long-wait rates?

Tabs/bookmarks: IMD / Ethnicity / Age / Sex.

Visuals: composition bars; observed-cell gap/ratio cards; provider heatmap; specialty composition; suppression-rate/data-completeness indicator. Every chart subtitle states whether it is composition or a denominator-adjusted rate.

Banner: **“WLMDS management information; small cells are suppressed and remaining values may be rounded. Larger waiting-list share does not by itself mean worse care.”**

## Page 6 — Geographic Intelligence

**Question:** Where is pressure geographically concentrated at valid organisation/system geographies?

Visuals: region/ICB benchmark matrix and map only for valid geographic entities. Provider points are not converted into provider-population rates unless a defensible catchment denominator exists.

## Page 7 — Provider Drill-through

Provider header: name, ODS code, organisation type/status, latest period, DQ state.

Visuals: 24-36 month backlog trend; 18-week and >52-week performance vs national; new vs completed pathways; backlog per completion; specialty drivers; demographic composition/gaps where eligible; quarterly KH03 proxy; recent DQ flags.

## Page 8 — Methodology & Data Quality

Show latest refresh/extraction time, source classifications, revision status, provider submissions/missingness, suppression rules, failed/warning checks, metric definitions and key limitations. Link to repository methodology/source register.

## Current prototype screenshots

The committed SVG prototypes use only the verified NHS England gateway snapshot and are labelled accordingly. They demonstrate visual intent, not a claim that all bulk analytical pages were executed in the restricted build environment.
