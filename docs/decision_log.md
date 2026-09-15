# Analytical decision log

| Decision | Rationale |
|---|---|
| RTT official statistics are the headline source | NHS England labels monthly RTT as Accredited Official Statistics and explicitly recommends official statistics over WLMDS management information for headline figures. |
| WLMDS used for demographic/detail analysis only | It provides age, sex, ethnicity and IMD detail unavailable in headline RTT, but has greater completeness/validation limitations. |
| Suppressed demographic cells stay null + status | Replacing `*` with zero or reverse-engineering cells would be analytically wrong and could undermine disclosure control. |
| No direct RTT↔KH03 specialty mapping | RTT treatment function and KH03 consultant-main-specialty are different classifications; no defensible one-to-one mapping was established. |
| KH03 availability and occupancy are separate facts | Official KH03 guidance reports available bed days by sector but occupied bed days by consultant main specialty; combining them at specialty grain would imply a denominator that is not published. |
| Bed data labelled a capacity proxy | Beds do not capture theatres, workforce, diagnostics, outpatient slots, case mix or all elective constraints. |
| No population-standardised provider rate by default | Provider catchments do not equal local-authority/LSOA populations. |
| Equal-weight score code retained but score not published | Equal weights are interpretable, but the full underlying components were not executed in the restricted runtime; publishing a partial composite would be misleading. |
| Forecast withheld in executed snapshot | Twelve observations do not meet the 24-month minimum-history gate. |
| Acute-provider gateway ranks not used as findings | Observed internal inconsistency in rank denominator/display; metric values are used only as verification evidence. |
