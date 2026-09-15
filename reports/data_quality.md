# Data quality report

## Build-level results

- Automated tests executed in this environment: **44 passed, 0 failed**.
- Verified NHS England gateway timeseries: **48 rows**, 12 months × 4 entities, with no duplicate `reporting_month × entity` keys.
- Selected July 2026 provider benchmark extract: **14 rows**.
- July 2026 national verification: 65.4% within 18 weeks and 1.5% over 52 weeks, matching the NHS England public gateway.
- Suppression parser explicitly distinguishes observed zero, suppressed, missing and not-applicable values.

## Known source-quality issues that the pipeline must preserve

1. WLMDS is management information and NHS England states it is subject to less validation than monthly official RTT statistics. Missing submissions can affect detailed outputs.
2. WLMDS demographic small cells are masked and unsuppressed values rounded; these are not exact raw counts.
3. RTT publications can be revised. Source URL/checksum/extraction time are retained so revised files can be detected.
4. NHS England notes unreported removals as an active RTT data-quality topic. New starts minus recorded completions therefore does not necessarily equal the observed waiting-list change.
5. Organisation codes/names can change after mergers/restructures; ODS mappings are time-aware rather than overwritten.
6. KH03 uses consultant-main-specialty while RTT uses treatment function. The project does not perform a speculative specialty-level join.
7. The NHS England acute provider gateway inspected during this build displayed an internal ranking inconsistency for the 18-week metric: it stated 107 ranked providers while some table rows displayed ranks greater than 107. The verification extract therefore retains metric values but does not use those anomalous displayed ranks as analytical evidence.
8. On the Northumbria provider page, the current >52-week card displayed “No data available” while its 12-month table and the acute-provider table showed 0.0%. The project uses the explicit tabular 0.0% in the verification fixture and records this presentation inconsistency as a quality note.
9. NHS England’s acute provider table warns that some latest provider values can be provisional/estimated and excludes some specialist providers from ranks; the selected extract is for demonstration/verification rather than a formal league table.

## Automated checks in full refresh

- duplicate composite keys;
- required identifiers/dates;
- non-negative counts;
- numeric conversion failures;
- unexpected wait bands/schema drift;
- valid ODS provider codes;
- referential integrity;
- date/month completeness;
- missing provider submissions;
- suppressed demographic status handling;
- extreme MoM changes for investigation;
- national/provider reconciliation against published totals;
- SQL/Python/DAX metric reconciliation.

Suspicious records are quarantined/flagged for review; they are not silently deleted merely because they look unusual.
