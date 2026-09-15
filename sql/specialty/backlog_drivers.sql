-- Treatment functions contributing most to national backlog change.
WITH monthly AS (
    SELECT
        reporting_month,
        treatment_function_code,
        SUM(total_incomplete) AS backlog
    FROM fact_rtt_waiting_list
    WHERE treatment_function_code <> 'TOTAL'
    GROUP BY 1,2
), changes AS (
    SELECT
        *,
        backlog - LAG(backlog) OVER (
            PARTITION BY treatment_function_code ORDER BY reporting_month
        ) AS backlog_change
    FROM monthly
), latest AS (
    SELECT * FROM changes
    QUALIFY reporting_month = MAX(reporting_month) OVER ()
)
SELECT
    l.*,
    s.treatment_function_name,
    backlog_change / NULLIF(SUM(backlog_change) OVER (), 0) AS share_of_net_national_change,
    DENSE_RANK() OVER (ORDER BY backlog_change DESC) AS growth_driver_rank
FROM latest l
LEFT JOIN dim_specialty s USING (treatment_function_code)
ORDER BY growth_driver_rank;
