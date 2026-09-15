-- Transparent screening percentiles. Composite score remains disabled until all components pass DQ.
WITH latest AS (
    SELECT *
    FROM mart_provider_monthly
    QUALIFY reporting_month = MAX(reporting_month) OVER ()
), percentiles AS (
    SELECT
        *,
        PERCENT_RANK() OVER (ORDER BY backlog_per_monthly_completion) AS backlog_to_throughput_percentile,
        PERCENT_RANK() OVER (ORDER BY long_wait_52_rate) AS long_wait_rate_percentile,
        PERCENT_RANK() OVER (ORDER BY demand_throughput_ratio) AS demand_throughput_percentile,
        NTILE(10) OVER (ORDER BY total_incomplete DESC) AS backlog_decile_desc
    FROM latest
)
SELECT * FROM percentiles
ORDER BY long_wait_rate_percentile DESC, demand_throughput_percentile DESC;
