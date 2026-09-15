# Health inequality analysis

## Available official detail

NHS England publishes WLMDS demographic breakdowns by age, sex, ethnicity and Index of Multiple Deprivation decile from July 2025. It classifies WLMDS as management information and warns that lower-granularity data quality may vary.

## Disclosure control

The processing layer preserves `observed`, `suppressed`, `missing` and `not_applicable` states. Published `*` cells never become zero. Values remaining after suppression may be rounded to the nearest five, so derived ratios/gaps must not be presented with spurious decimal precision.

## Interpretation rules

- A larger share of a waiting list for one group does not by itself mean worse care; underlying population size, age structure, healthcare need, referral patterns and provider catchment can all contribute.
- Without compatible denominators, results are labelled **waiting-list composition** rather than population prevalence/rates.
- Provider catchments are not assumed to equal local-authority or LSOA populations.
- ONS denominators are introduced only where numerator geography and denominator population are compatible.
- Aggregate provider/geographic associations are not patient-level effects and cannot establish discrimination or causation.

## Planned full-refresh outputs

When the WLMDS CSV files are available to the pipeline, the analytical mart can produce observed-cell-only most-vs-least deprived gaps, long-wait rate differences/ratios where compatible numerators/denominators exist, demographic waiting-list shares, provider percentiles and specialty comparisons. Any result depending on a suppressed cell is returned as unavailable rather than inferred.

## Executed-build status

The current restricted execution runtime could inspect the WLMDS publication page but could not download the CSV/XLSX attachments. Therefore **no demographic inequality numerical finding is claimed in this build**. This is an explicit analytical quality decision, not missing documentation.
