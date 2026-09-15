# Data dictionary

This warehouse deliberately separates accredited RTT official statistics from WLMDS management information. It does not treat pathway counts as unique patients.

| Table | Grain / primary key | Business meaning | Source / important transformations |
|---|---|---|---|
| `dim_date` | One row per calendar date | Date attributes used by Power BI and SQL time intelligence | Generated locally; month-end flag supports monthly facts. |
| `dim_provider` | One ODS provider code | NHS organisation reference dimension | ODS/DSE/ORD. Status and successor fields preserve organisational change context. |
| `dim_specialty` | One RTT treatment-function code | RTT treatment-function reference | NHS RTT reference metadata. `is_total` explicitly distinguishes the published Total row from specialty detail, preventing provider-level double counting. No forced mapping to KH03 consultant specialties. |
| `dim_wait_band` | One published wait band | Ordered waiting-time categories | RTT publication definitions. |
| `dim_demographic` | One dimension/category combination | WLMDS age, sex, ethnicity or other published categories | WLMDS. Labels are retained as published. |
| `dim_deprivation` | IMD decile 1-10 | Deprivation grouping | WLMDS published IMD decile; decile 1 is most deprived, 10 least deprived. |
| `fact_rtt_waiting_list` | Month × provider × treatment function × source file | Official RTT incomplete-pathway counts and long-wait fields | Accredited RTT official statistics. Revised files supersede older extracts only after provenance comparison. |
| `fact_rtt_activity` | Month × provider × treatment function × source file | New RTT periods and admitted/non-admitted completed pathways | Official RTT activity. Completed pathways combine admitted + non-admitted only where both fields are present at the same grain. |
| `fact_wlmds_pathways` | Observation date × provider × treatment function × source file | WLMDS open/new/completed management-information measures | Management information; missing submissions are not silently estimated. |
| `fact_wlmds_demographics` | Observation × provider × specialty × dimension × category × measure × file | Published demographic aggregate counts/status | Suppressed cells are stored with `value=NULL`, `value_status='suppressed'`; never replaced by zero. |
| `fact_bed_availability` | Quarter × provider × availability sector × bed type × file | KH03 available bed days | Availability is reported by sector; kept separate from consultant-specialty occupancy. Capacity proxy only. |
| `fact_bed_occupancy` | Quarter × provider × consultant main specialty × bed type × file | KH03 occupied bed days | Occupancy detail is retained at its published specialty grain; it is not mapped to RTT treatment function. |
| `data_quality_results` | Run × dataset × period × check | Audit trail of validation results | Failing observations are flagged for investigation rather than deleted. |
| `source_registry` | Dataset × URL × extraction time | Provenance/revision register | Stores publisher, source classification, checksum and publication period. |
| `mart_provider_monthly` | Month × provider | Provider-level operational screening metrics | Derived only from RTT treatment-function `TOTAL` rows so specialty detail is not double-counted; ratios use `NULLIF` to avoid divide-by-zero. |

## Value-status contract

WLMDS demographic values use `observed`, `suppressed`, `missing`, or `not_applicable`. Only `observed` values are eligible for precise ratios/rankings. Suppressed counts are never reverse-engineered from totals.
