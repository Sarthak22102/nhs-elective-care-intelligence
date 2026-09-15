-- Provider monthly waiting-list and flow KPIs with MoM/YoY/rolling comparisons.
WITH base AS (
    SELECT * FROM mart_provider_monthly
), lagged AS (
    SELECT
        *,
        LAG(total_incomplete, 1) OVER (PARTITION BY provider_code ORDER BY reporting_month) AS backlog_prev_month,
        LAG(total_incomplete, 12) OVER (PARTITION BY provider_code ORDER BY reporting_month) AS backlog_prev_year,
        AVG(new_rtt_periods) OVER (
            PARTITION BY provider_code ORDER BY reporting_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_3m_demand,
        AVG(completed_pathways) OVER (
            PARTITION BY provider_code ORDER BY reporting_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_3m_throughput
    FROM base
)
SELECT
    *,
    total_incomplete - backlog_prev_month AS backlog_mom_change,
    (total_incomplete - backlog_prev_month) / NULLIF(backlog_prev_month, 0) AS backlog_mom_pct,
    total_incomplete - backlog_prev_year AS backlog_yoy_change,
    (total_incomplete - backlog_prev_year) / NULLIF(backlog_prev_year, 0) AS backlog_yoy_pct,
    rolling_3m_demand / NULLIF(rolling_3m_throughput, 0) AS rolling_3m_demand_throughput_ratio
FROM lagged;
