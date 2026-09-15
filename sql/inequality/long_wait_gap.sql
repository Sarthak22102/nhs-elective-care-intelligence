-- Template for long-wait rate gaps only when WLMDS publishes compatible observed numerator/denominator cells.
WITH observed AS (
    SELECT * FROM fact_wlmds_demographics WHERE value_status = 'observed'
), rates AS (
    SELECT
        reporting_month, provider_code, treatment_function_code, dimension_name, category_label,
        SUM(CASE WHEN measure_name = 'long_wait_pathways' THEN value END)
          / NULLIF(SUM(CASE WHEN measure_name = 'open_pathways' THEN value END), 0) AS long_wait_rate
    FROM observed
    GROUP BY 1,2,3,4,5
)
SELECT * FROM rates WHERE long_wait_rate IS NOT NULL;
