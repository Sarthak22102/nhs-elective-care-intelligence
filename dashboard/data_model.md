# Power BI semantic model specification

## Model shape

Use a star schema. Relationships are single-direction from dimensions to facts unless a documented use case proves otherwise.

| From (1) | To (*) | Key | Direction | Active |
|---|---|---|---|---|
| `dim_date` | `fact_rtt_waiting_list` | `date_key` → `reporting_month` | Single | Yes |
| `dim_date` | `fact_rtt_activity` | `date_key` → `reporting_month` | Single | Yes |
| `dim_date` | `fact_wlmds_pathways` | `date_key` → `reporting_month` | Single | Yes |
| `dim_date` | `fact_wlmds_demographics` | `date_key` → `reporting_month` | Single | Yes |
| `dim_date` | `fact_bed_availability` | `date_key` → `quarter_end` | Single | Yes |
| `dim_date` | `fact_bed_occupancy` | `date_key` → `quarter_end` | Single | Yes |
| `dim_provider` | all provider facts | `provider_code` | Single | Yes |
| `dim_specialty` | RTT/WLMDS facts | `treatment_function_code` | Single | Yes |
| `dim_demographic` | demographic fact | dimension/category key | Single | Yes |
| `dim_deprivation` | demographic mart where applicable | IMD decile | Single | Yes |

Do **not** directly relate KH03 consultant-main-specialty to RTT treatment function. KH03 availability and occupancy are separate facts because their published detail grains differ. Capacity ratios should use provider/quarter/bed-type context; disable RTT specialty interactions on those visuals unless an externally validated crosswalk is later added.

## Date dimension

Mark `dim_date[date_key]` as the date table. Hide numeric month/year sort fields from report view. `month_name` sorts by `month`; `year_month` sorts by `date_key`.

## Hierarchies

- Date: Year → Quarter → Month
- Provider geography when validated: Region → ICB → Provider
- Specialty: Specialty group → Treatment function
- Demographic: Dimension → Category

## Hidden technical fields

Hide source filenames, hashes, extraction timestamps, surrogate/composite technical keys and raw status codes from report consumers; expose them only on the methodology/data-quality page where relevant.

## Measures vs calculated columns

Business calculations should be DAX measures. Calculated columns are limited to stable semantic labels/sorts that cannot be better produced upstream. Pressure-score components should be materialised in the analytical mart with transparent contributions so Power BI is not the only place the logic exists.

## Row-level model cautions

This is public aggregate data; no user-specific row-level security is required for the portfolio. If deployed operationally, security requirements must be reassessed independently.
