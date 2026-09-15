"""Locally runnable public-aggregate analytical interface.

When a full processed mart is available it should be substituted for the small
committed verification snapshot. The app deliberately labels its current scope.
"""
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/reference/official_gateway_elective_timeseries.csv"
SNAP = ROOT / "data/reference/official_gateway_selected_provider_snapshot.csv"

st.set_page_config(page_title="NHS Elective Care Intelligence", layout="wide")
st.title("NHS Elective Care Intelligence")
st.caption("Public aggregate decision-support portfolio • current app uses a verified NHS England gateway snapshot")

@st.cache_data
def load_data():
    ts = pd.read_csv(DATA, parse_dates=["reporting_month"])
    snap = pd.read_csv(SNAP)
    return ts, snap

ts, snap = load_data()
latest = ts[ts["reporting_month"] == ts["reporting_month"].max()]
nat = latest[latest["entity_type"] == "national"].iloc[0]

c1,c2,c3 = st.columns(3)
c1.metric("England within 18 weeks", f"{nat.within_18_weeks_pct:.1f}%", "Jul 2026")
c2.metric("England over 52 weeks", f"{nat.over_52_weeks_pct:.1f}%", "Jul 2026")
c3.metric("Verified records", f"{len(ts)+len(snap):,}", "prototype scope")

st.subheader("12-month elective performance")
metric = st.radio("Metric", ["Within 18 weeks", "Over 52 weeks"], horizontal=True)
col = "within_18_weeks_pct" if metric == "Within 18 weeks" else "over_52_weeks_pct"
pivot = ts.pivot(index="reporting_month", columns="entity", values=col)
st.line_chart(pivot)

st.subheader("Selected provider benchmark — July 2026")
show = snap[["provider","within_18_weeks_pct","over_52_weeks_pct"]].sort_values("within_18_weeks_pct", ascending=False)
st.dataframe(show, use_container_width=True, hide_index=True)

st.info(
    "This interface does not publish provider pressure scores, inequality gaps, capacity relationships or forecasts "
    "until the full official source files are ingested and validated. WLMDS demographic data are management information "
    "and suppressed cells must never be reconstructed."
)
