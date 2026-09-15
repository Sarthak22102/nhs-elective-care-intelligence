-- NHS Elective Care Intelligence analytical warehouse (DuckDB)
-- Public aggregate data only. Pathway counts must not be described as unique patients.

CREATE TABLE IF NOT EXISTS dim_date (
    date_key DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR NOT NULL,
    year_month VARCHAR NOT NULL,
    month_end BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_provider (
    provider_code VARCHAR PRIMARY KEY,
    provider_name VARCHAR,
    organisation_type VARCHAR,
    status VARCHAR,
    region_name VARCHAR,
    icb_code VARCHAR,
    icb_name VARCHAR,
    address VARCHAR,
    postcode VARCHAR,
    open_date DATE,
    close_date DATE,
    successor_provider_code VARCHAR,
    source_effective_date DATE,
    source_url VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_specialty (
    treatment_function_code VARCHAR PRIMARY KEY,
    treatment_function_name VARCHAR,
    specialty_group VARCHAR,
    is_total BOOLEAN NOT NULL DEFAULT FALSE,
    source_url VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_wait_band (
    wait_band_key VARCHAR PRIMARY KEY,
    lower_weeks INTEGER,
    upper_weeks INTEGER,
    open_ended BOOLEAN,
    sort_order INTEGER
);

CREATE TABLE IF NOT EXISTS dim_demographic (
    demographic_key VARCHAR PRIMARY KEY,
    dimension_name VARCHAR NOT NULL,
    category_code VARCHAR,
    category_label VARCHAR NOT NULL,
    sort_order INTEGER
);

CREATE TABLE IF NOT EXISTS dim_deprivation (
    imd_decile INTEGER PRIMARY KEY,
    deprivation_label VARCHAR NOT NULL,
    most_deprived_flag BOOLEAN NOT NULL,
    least_deprived_flag BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_rtt_waiting_list (
    reporting_month DATE NOT NULL,
    provider_code VARCHAR NOT NULL,
    treatment_function_code VARCHAR NOT NULL,
    total_incomplete DOUBLE,
    within_18_weeks DOUBLE,
    over_52_weeks DOUBLE,
    over_65_weeks DOUBLE,
    over_78_weeks DOUBLE,
    over_104_weeks DOUBLE,
    decision_to_admit_incomplete DOUBLE,
    estimated_or_submitted VARCHAR,
    source_file VARCHAR NOT NULL,
    source_sha256 VARCHAR,
    extraction_timestamp TIMESTAMP,
    PRIMARY KEY (reporting_month, provider_code, treatment_function_code, source_file)
);

CREATE TABLE IF NOT EXISTS fact_rtt_activity (
    reporting_month DATE NOT NULL,
    provider_code VARCHAR NOT NULL,
    treatment_function_code VARCHAR NOT NULL,
    new_rtt_periods DOUBLE,
    admitted_completed DOUBLE,
    non_admitted_completed DOUBLE,
    source_file VARCHAR NOT NULL,
    source_sha256 VARCHAR,
    extraction_timestamp TIMESTAMP,
    PRIMARY KEY (reporting_month, provider_code, treatment_function_code, source_file)
);

CREATE TABLE IF NOT EXISTS fact_wlmds_pathways (
    observation_date DATE NOT NULL,
    reporting_month DATE NOT NULL,
    provider_code VARCHAR NOT NULL,
    treatment_function_code VARCHAR,
    open_pathways DOUBLE,
    new_pathways DOUBLE,
    completed_pathways DOUBLE,
    first_attendance_within_18_weeks DOUBLE,
    value_status VARCHAR DEFAULT 'observed',
    submitted_flag BOOLEAN,
    source_file VARCHAR NOT NULL,
    PRIMARY KEY (observation_date, provider_code, treatment_function_code, source_file)
);

CREATE TABLE IF NOT EXISTS fact_wlmds_demographics (
    observation_date DATE NOT NULL,
    reporting_month DATE NOT NULL,
    provider_code VARCHAR,
    treatment_function_code VARCHAR,
    dimension_name VARCHAR NOT NULL,
    category_label VARCHAR NOT NULL,
    measure_name VARCHAR NOT NULL,
    value DOUBLE,
    value_status VARCHAR NOT NULL,
    source_file VARCHAR NOT NULL,
    PRIMARY KEY (
        observation_date, provider_code, treatment_function_code,
        dimension_name, category_label, measure_name, source_file
    )
);

CREATE TABLE IF NOT EXISTS fact_bed_availability (
    quarter_end DATE NOT NULL,
    provider_code VARCHAR NOT NULL,
    availability_sector VARCHAR NOT NULL,
    bed_type VARCHAR NOT NULL,
    available_bed_days DOUBLE NOT NULL,
    source_file VARCHAR NOT NULL,
    PRIMARY KEY (quarter_end, provider_code, availability_sector, bed_type, source_file)
);

CREATE TABLE IF NOT EXISTS fact_bed_occupancy (
    quarter_end DATE NOT NULL,
    provider_code VARCHAR NOT NULL,
    consultant_main_specialty VARCHAR NOT NULL,
    bed_type VARCHAR NOT NULL,
    occupied_bed_days DOUBLE NOT NULL,
    source_file VARCHAR NOT NULL,
    PRIMARY KEY (quarter_end, provider_code, consultant_main_specialty, bed_type, source_file)
);

CREATE TABLE IF NOT EXISTS data_quality_results (
    run_timestamp TIMESTAMP NOT NULL,
    dataset VARCHAR NOT NULL,
    reporting_period VARCHAR,
    check_name VARCHAR NOT NULL,
    severity VARCHAR NOT NULL,
    passed BOOLEAN NOT NULL,
    failed_rows BIGINT NOT NULL,
    detail VARCHAR
);

CREATE TABLE IF NOT EXISTS source_registry (
    dataset_name VARCHAR NOT NULL,
    source_url VARCHAR NOT NULL,
    publisher VARCHAR NOT NULL,
    classification VARCHAR NOT NULL,
    publication_period VARCHAR,
    extraction_timestamp TIMESTAMP,
    source_sha256 VARCHAR,
    revision_note VARCHAR,
    PRIMARY KEY (dataset_name, source_url, extraction_timestamp)
);

CREATE OR REPLACE VIEW mart_provider_monthly AS
SELECT
    w.reporting_month,
    w.provider_code,
    p.provider_name,
    SUM(w.total_incomplete) AS total_incomplete,
    SUM(w.within_18_weeks) AS within_18_weeks,
    SUM(w.over_52_weeks) AS over_52_weeks,
    SUM(a.new_rtt_periods) AS new_rtt_periods,
    SUM(a.admitted_completed) AS admitted_completed,
    SUM(a.non_admitted_completed) AS non_admitted_completed,
    SUM(a.admitted_completed) + SUM(a.non_admitted_completed) AS completed_pathways,
    SUM(w.within_18_weeks) / NULLIF(SUM(w.total_incomplete), 0) AS performance_18_week,
    SUM(w.over_52_weeks) / NULLIF(SUM(w.total_incomplete), 0) AS long_wait_52_rate,
    SUM(a.new_rtt_periods) / NULLIF(SUM(a.admitted_completed) + SUM(a.non_admitted_completed), 0) AS demand_throughput_ratio,
    SUM(a.new_rtt_periods) - (SUM(a.admitted_completed) + SUM(a.non_admitted_completed)) AS net_pathway_pressure,
    SUM(w.total_incomplete) / NULLIF(SUM(a.admitted_completed) + SUM(a.non_admitted_completed), 0) AS backlog_per_monthly_completion
FROM fact_rtt_waiting_list w
LEFT JOIN fact_rtt_activity a
  ON w.reporting_month = a.reporting_month
 AND w.provider_code = a.provider_code
 AND w.treatment_function_code = a.treatment_function_code
LEFT JOIN dim_provider p ON w.provider_code = p.provider_code
WHERE w.treatment_function_code = 'TOTAL'
GROUP BY 1,2,3;
