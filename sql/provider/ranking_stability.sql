-- Month-to-month provider rank movement for long-wait rate.
WITH ranked AS (
    SELECT
        reporting_month,
        provider_code,
        provider_name,
        long_wait_52_rate,
        DENSE_RANK() OVER (PARTITION BY reporting_month ORDER BY long_wait_52_rate DESC) AS long_wait_rank
    FROM mart_provider_monthly
    WHERE long_wait_52_rate IS NOT NULL
), changes AS (
    SELECT
        *,
        LAG(long_wait_rank) OVER (PARTITION BY provider_code ORDER BY reporting_month) AS previous_rank
    FROM ranked
)
SELECT *, previous_rank - long_wait_rank AS rank_improvement
FROM changes
ORDER BY reporting_month DESC, ABS(previous_rank - long_wait_rank) DESC NULLS LAST;
