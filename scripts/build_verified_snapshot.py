#!/usr/bin/env python3
"""Build a small verified official-gateway snapshot used for CI/demo validation.

This is NOT a substitute for the bulk RTT/WLMDS pipeline. Values below are a
transparent transcription of NHS England Public Data Gateway tables, captured
15 September 2026, because this execution environment could read official HTML
but could not download NHS binary/CSV publication attachments.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/reference"
OUT.mkdir(parents=True, exist_ok=True)

months = pd.to_datetime([
    "2025-08-31","2025-09-30","2025-10-31","2025-11-30","2025-12-31",
    "2026-01-31","2026-02-28","2026-03-31","2026-04-30","2026-05-31",
    "2026-06-30","2026-07-31",
])
national_18 = [61.0,61.8,61.8,61.8,61.5,61.5,62.6,65.3,65.0,65.6,65.8,65.4]
national_52 = [2.6,2.4,2.3,2.1,1.9,1.9,1.7,1.3,1.4,1.4,1.5,1.5]
providers = {
    "Northumbria Healthcare NHS Foundation Trust": {
        "url":"https://data.england.nhs.uk/providers/northumbria-healthcare-nhs-foundation-trust",
        "within_18":[82.0,82.6,82.7,81.9,81.0,80.8,81.5,82.7,82.0,83.0,83.9,83.9],
        "over_52":[0.0]*12,
    },
    "Royal Berkshire NHS Foundation Trust": {
        "url":"https://data.england.nhs.uk/providers/royal-berkshire-nhs-foundation-trust",
        "within_18":[79.7,80.9,81.4,81.7,82.2,83.5,82.2,83.8,83.4,83.1,84.4,83.3],
        "over_52":[0.1]*12,
    },
    "Mid And South Essex NHS Foundation Trust": {
        "url":"https://data.england.nhs.uk/providers/mid-and-south-essex-nhs-foundation-trust",
        "within_18":[50.6,50.6,49.9,49.2,48.2,49.1,50.4,50.6,49.3,50.3,49.7,49.8],
        "over_52":[7.8,8.0,8.0,7.9,7.6,7.7,7.1,7.0,7.0,7.1,7.5,7.9],
    },
}
rows=[]
for i,month in enumerate(months):
    rows.append({
        "reporting_month":month.date().isoformat(),"entity":"England national average","entity_type":"national",
        "within_18_weeks_pct":national_18[i],"over_52_weeks_pct":national_52[i],
        "source_url":"https://data.england.nhs.uk/providers/acute-provider-table",
        "source_system":"NHS England Public Data Gateway","captured_date":"2026-09-15"
    })
    for name,v in providers.items():
        rows.append({
            "reporting_month":month.date().isoformat(),"entity":name,"entity_type":"provider",
            "within_18_weeks_pct":v["within_18"][i],"over_52_weeks_pct":v["over_52"][i],
            "source_url":v["url"],"source_system":"NHS England Public Data Gateway","captured_date":"2026-09-15"
        })
pd.DataFrame(rows).to_csv(OUT/"official_gateway_elective_timeseries.csv",index=False)

selected = [
    ("Northumbria Healthcare NHS Foundation Trust",83.9,0.0),
    ("Royal Berkshire NHS Foundation Trust",83.3,0.1),
    ("East Suffolk and North Essex NHS Foundation Trust",59.7,0.5),
    ("North West Anglia NHS Foundation Trust",59.6,0.5),
    ("Bedfordshire Hospitals NHS Foundation Trust",59.1,1.2),
    ("Milton Keynes University Hospital NHS Foundation Trust",58.8,2.6),
    ("York and Scarborough Teaching Hospitals NHS Foundation Trust",58.5,2.0),
    ("University Hospitals Coventry and Warwickshire NHS Trust",58.3,3.7),
    ("Medway NHS Foundation Trust",58.0,2.1),
    ("Great Western Hospitals NHS Foundation Trust",57.9,2.5),
    ("Hull University Teaching Hospitals NHS Trust",56.0,3.9),
    ("Northern Care Alliance NHS Foundation Trust",55.9,2.8),
    ("East Kent Hospitals University NHS Foundation Trust",55.2,3.2),
    ("Mid And South Essex NHS Foundation Trust",49.8,7.9),
]
snap=pd.DataFrame(selected,columns=["provider","within_18_weeks_pct","over_52_weeks_pct"])
snap["reporting_month"]="2026-07-31"
snap["national_within_18_weeks_pct"]=65.4
snap["national_over_52_weeks_pct"]=1.5
snap["source_url"]="https://data.england.nhs.uk/providers/acute-provider-table"
snap["source_system"]="NHS England Public Data Gateway"
snap["captured_date"]="2026-09-15"
snap.to_csv(OUT/"official_gateway_selected_provider_snapshot.csv",index=False)
print(f"Wrote {len(rows)} time-series records and {len(snap)} selected-provider records.")
