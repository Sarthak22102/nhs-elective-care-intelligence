-- Providers where backlog has increased in consecutive months.
WITH monthly AS (
    SELECT
        reporting_month,
        provider_code,
        provider_name,
        total_incomplete,
        LAG(total_incomplete) OVER (PARTITION BY provider_code ORDER BY reporting_month) AS previous_backlog
    FROM mart_provider_monthly
), flags AS (
    SELECT *, CASE WHEN total_incomplete > previous_backlog THEN 1 ELSE 0 END AS deteriorating
    FROM monthly
), groups AS (
    SELECT *,
        SUM(CASE WHEN deteriorating = 0 THEN 1 ELSE 0 END)
        OVER (PARTITION BY provider_code ORDER BY reporting_month) AS streak_group
    FROM flags
), streaks AS (
    SELECT *,
        SUM(deteriorating) OVER (PARTITION BY provider_code, streak_group ORDER BY reporting_month) AS consecutive_growth_months
    FROM groups
)
SELECT *
FROM streaks
WHERE consecutive_growth_months >= 3
ORDER BY reporting_month DESC, consecutive_growth_months DESC, total_incomplete DESC;
