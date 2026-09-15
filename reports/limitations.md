# Limitations

1. **RTT pathways are not necessarily unique patients.** One person can have more than one referral/pathway; project wording therefore uses pathways unless an official source explicitly reports people.
2. **RTT definitions and clock rules matter.** Incomplete, completed admitted, completed non-admitted, decision-to-admit and new RTT periods are different measures and are not interchangeable.
3. **Revisions occur.** Historical releases can be revised; provenance/checksums are required for reproducible comparisons.
4. **Recorded starts/completions do not fully explain stock movement.** NHS England highlights unreported removals as a data-quality issue, so a simple flow identity can have a residual.
5. **Provider reporting/data quality varies.** Missing/late submissions and adjustments can affect apparent trends.
6. **WLMDS is management information.** It is subject to less central validation than monthly official RTT statistics and should not replace RTT for headline totals.
7. **Demographic suppression/rounding limits precision.** Small values are masked and remaining values may be rounded; suppressed values are never reconstructed.
8. **Provider structures change.** Mergers, closures, successors and code changes can create artificial breaks if ODS effective dates are ignored.
9. **Provider catchments complicate population rates.** A hospital trust is not a simple geographic population denominator; local-authority/LSOA denominators cannot be attached without a defensible population mapping.
10. **KH03 is not total elective capacity.** Beds are one operational resource; theatres, workforce, diagnostics, outpatient capacity and case mix are not captured by bed days alone. Available beds are published by sector while occupied beds are broken down by consultant main specialty, so this project only forms occupancy proxies after separate provider-level aggregation.
11. **Specialty definitions differ.** KH03 consultant main specialty is not automatically equivalent to RTT treatment function.
12. **Pandemic comparability.** NHS England specifically warns that 2020/21 bed occupancy is not directly comparable in the usual way because capacity was organised differently.
13. **Aggregate analysis risks ecological fallacy.** Provider/group associations cannot be assigned to individuals and do not demonstrate causal mechanisms.
14. **Forecasts are uncertain.** Structural breaks, policy changes, industrial action, coding/reporting changes and capacity interventions can make past patterns unstable; the build therefore gates forecasting on history/data quality.
15. **Verification snapshot is deliberately narrow.** The executed 62 committed verification records support only the findings stated in `reports/findings.md`. They are not used to imply full national provider/specialty coverage.
16. **Runtime acquisition limitation.** During this build, the official NHS publication pages were accessible but the execution container could not fetch binary/CSV attachments. Full-source metrics are therefore implemented but not falsely reported as executed.
