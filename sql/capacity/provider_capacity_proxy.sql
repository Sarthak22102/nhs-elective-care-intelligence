-- Provider-level KH03 bed proxy. Do not interpret as total elective capacity.
-- KH03 availability is reported by sector, while occupancy is reported by consultant
-- main specialty. They are therefore aggregated separately to provider/quarter/bed type
-- before a provider-level ratio is formed. No specialty-level capacity ratio is produced.
WITH availability AS (
    SELECT
        quarter_end,
        provider_code,
        bed_type,
        SUM(available_bed_days) AS available_bed_days
    FROM fact_bed_availability
    GROUP BY 1,2,3
), occupancy AS (
    SELECT
        quarter_end,
        provider_code,
        bed_type,
        SUM(occupied_bed_days) AS occupied_bed_days
    FROM fact_bed_occupancy
    GROUP BY 1,2,3
), beds AS (
    SELECT
        COALESCE(a.quarter_end, o.quarter_end) AS quarter_end,
        COALESCE(a.provider_code, o.provider_code) AS provider_code,
        COALESCE(a.bed_type, o.bed_type) AS bed_type,
        a.available_bed_days,
        o.occupied_bed_days,
        o.occupied_bed_days / NULLIF(a.available_bed_days, 0) AS bed_occupancy
    FROM availability a
    FULL OUTER JOIN occupancy o USING (quarter_end, provider_code, bed_type)
), activity AS (
    SELECT
        DATE_TRUNC('quarter', reporting_month) + INTERVAL '3 months' - INTERVAL '1 day' AS quarter_end,
        provider_code,
        SUM(admitted_completed + non_admitted_completed) AS completed_pathways
    FROM fact_rtt_activity
    WHERE treatment_function_code = 'TOTAL'
    GROUP BY 1,2
)
SELECT
    b.quarter_end,
    b.provider_code,
    p.provider_name,
    b.bed_type,
    b.available_bed_days,
    b.occupied_bed_days,
    b.bed_occupancy,
    a.completed_pathways,
    a.completed_pathways / NULLIF(b.available_bed_days, 0) AS completions_per_available_bed_day
FROM beds b
LEFT JOIN activity a USING (quarter_end, provider_code)
LEFT JOIN dim_provider p USING (provider_code);
