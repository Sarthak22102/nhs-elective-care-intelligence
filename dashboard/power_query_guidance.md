# Power Query / data-load guidance

Preferred production pattern: Python/DuckDB performs extraction, cleaning and calculations; Power BI imports clean dimension/fact/mart outputs. Keep Power Query lightweight and auditable.

1. Parameterise the repository/processed-data root rather than using an analyst-specific absolute path.
2. Import Parquet/CSV exports for dimensions and marts; assign explicit data types.
3. Disable load for staging queries.
4. Do not re-implement suppression parsing in Power Query; use upstream `value_status`.
5. Do not create many-to-many/bidirectional relationships to work around model issues.
6. Preserve provider codes as text (including any leading characters/zeroes).
7. Refresh date is sourced from the model/source registry, not typed into a text box.
8. Any row filtering that removes invalid records must be justified by the DQ report rather than hidden in UI steps.
