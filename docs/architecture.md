# Architecture

```mermaid
flowchart LR
    A[NHS England RTT\nAccredited Official Statistics] --> E[Python discovery + download\nURL / checksum / extraction metadata]
    B[WLMDS\nManagement Information] --> E
    C[KH03 Bed Availability + Occupancy\nQuarterly; separate grains] --> E
    D[ODS + ONS\nReference / denominators] --> E
    E --> F[Raw immutable cache]
    F --> G[Schema standardisation\nSuppression-aware cleaning]
    G --> H[Automated data-quality checks]
    H --> I[(DuckDB analytical warehouse)]
    I --> J[SQL marts\nWindows / lags / ranks / rolling flow]
    J --> K[Python statistics\nforecast readiness / sensitivity]
    J --> L[Power BI star-schema exports]
    J --> M[Streamlit analytical interface]
    K --> N[Findings + methodology]
    L --> O[Executive dashboard specification]
```

The source hierarchy is intentional: RTT supplies headline official statistics; WLMDS adds detail; KH03 adds separately modelled availability/occupancy series for provider-level bed proxies; ODS stabilises organisation identities; ONS is optional for compatible denominator analyses.
