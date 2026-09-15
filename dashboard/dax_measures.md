# DAX measure library

These measures assume the star schema documented in `data_model.md`. Measures that require full RTT/WLMDS/KH03 facts should remain hidden/disabled until the relevant quality gate passes.

```DAX
Total Waiting List =
SUM ( fact_rtt_waiting_list[total_incomplete] )

Within 18 Weeks =
SUM ( fact_rtt_waiting_list[within_18_weeks] )

18 Week Performance =
DIVIDE ( [Within 18 Weeks], [Total Waiting List] )

Long Wait 52+ Pathways =
SUM ( fact_rtt_waiting_list[over_52_weeks] )

Long Wait 52+ % =
DIVIDE ( [Long Wait 52+ Pathways], [Total Waiting List] )

New RTT Pathways =
SUM ( fact_rtt_activity[new_rtt_periods] )

Admitted Completions =
SUM ( fact_rtt_activity[admitted_completed] )

Non-Admitted Completions =
SUM ( fact_rtt_activity[non_admitted_completed] )

Completed Pathways =
[Admitted Completions] + [Non-Admitted Completions]

Demand Throughput Ratio =
DIVIDE ( [New RTT Pathways], [Completed Pathways] )

Clearance Ratio =
DIVIDE ( [Completed Pathways], [New RTT Pathways] )

Net Pathway Pressure =
[New RTT Pathways] - [Completed Pathways]

Backlog per Monthly Completion =
DIVIDE ( [Total Waiting List], [Completed Pathways] )

Waiting List MoM Change =
VAR Previous = CALCULATE ( [Total Waiting List], DATEADD ( dim_date[date_key], -1, MONTH ) )
RETURN [Total Waiting List] - Previous

Waiting List MoM % =
VAR Previous = CALCULATE ( [Total Waiting List], DATEADD ( dim_date[date_key], -1, MONTH ) )
RETURN DIVIDE ( [Total Waiting List] - Previous, Previous )

Waiting List YoY Change =
VAR Previous = CALCULATE ( [Total Waiting List], DATEADD ( dim_date[date_key], -1, YEAR ) )
RETURN [Total Waiting List] - Previous

Waiting List YoY % =
VAR Previous = CALCULATE ( [Total Waiting List], DATEADD ( dim_date[date_key], -1, YEAR ) )
RETURN DIVIDE ( [Total Waiting List] - Previous, Previous )

Rolling 3M Demand =
CALCULATE (
    [New RTT Pathways],
    DATESINPERIOD ( dim_date[date_key], MAX ( dim_date[date_key] ), -3, MONTH )
)

Rolling 3M Throughput =
CALCULATE (
    [Completed Pathways],
    DATESINPERIOD ( dim_date[date_key], MAX ( dim_date[date_key] ), -3, MONTH )
)

Rolling 3M Demand Throughput Ratio =
DIVIDE ( [Rolling 3M Demand], [Rolling 3M Throughput] )

Provider Share of National Waiting List =
DIVIDE (
    [Total Waiting List],
    CALCULATE ( [Total Waiting List], REMOVEFILTERS ( dim_provider ) )
)

National 18 Week Benchmark =
CALCULATE ( [18 Week Performance], REMOVEFILTERS ( dim_provider ) )

18 Week Benchmark Difference =
[18 Week Performance] - [National 18 Week Benchmark]

Provider Long Wait Rank =
RANKX (
    ALLSELECTED ( dim_provider[provider_name] ),
    [Long Wait 52+ %],,
    DESC,
    Dense
)

Available Bed Days =
SUM ( fact_bed_availability[available_bed_days] )

Occupied Bed Days =
SUM ( fact_bed_occupancy[occupied_bed_days] )

Bed Occupancy Proxy =
DIVIDE ( [Occupied Bed Days], [Available Bed Days] )

Completions per Available Bed-Day =
DIVIDE ( [Completed Pathways], [Available Bed Days] )
```

## Suppression-safe inequality measures

Build the demographic analytical mart upstream so suppressed cells have `value=NULL` and are excluded from eligible observed-cell measures. Do not create a DAX expression that converts blanks from suppressed cells to zero.

```DAX
Observed Demographic Value =
CALCULATE (
    SUM ( fact_wlmds_demographics[value] ),
    fact_wlmds_demographics[value_status] = "observed"
)
```

Most/least deprived gaps should use explicit category filters only after verifying that the source uses compatible measures and both cells are observed. The data-quality page should display the number/share of suppressed cells alongside any inequality visual.


**KH03 filter rule:** Bed occupancy/capacity-proxy visuals must be evaluated at provider/quarter/bed-type grain. RTT treatment-function filters must not be allowed to imply specialty-level bed availability, because KH03 available beds are published by sector while occupied beds are broken down by consultant main specialty.
