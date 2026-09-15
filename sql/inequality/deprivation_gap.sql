-- Most-deprived vs least-deprived published WLMDS comparison.
-- Only observed cells are used; suppressed/missing values never enter the ratio.
WITH observed AS (
    SELECT *
    FROM fact_wlmds_demographics
    WHERE dimension_name = 'imd_decile'
      AND value_status = 'observed'
), pivoted AS (
    SELECT
        reporting_month,
        provider_code,
        treatment_function_code,
        measure_name,
        SUM(CASE WHEN category_label IN ('1', 'Decile 1', '1 - most deprived') THEN value END) AS most_deprived,
        SUM(CASE WHEN category_label IN ('10', 'Decile 10', '10 - least deprived') THEN value END) AS least_deprived
    FROM observed
    GROUP BY 1,2,3,4
)
SELECT
    *,
    most_deprived - least_deprived AS absolute_count_gap,
    most_deprived / NULLIF(least_deprived, 0) AS composition_ratio
FROM pivoted
WHERE most_deprived IS NOT NULL AND least_deprived IS NOT NULL;
