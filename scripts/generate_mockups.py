#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dashboard/screenshots'
OUT.mkdir(parents=True,exist_ok=True)
ts=pd.read_csv(ROOT/'data/reference/official_gateway_elective_timeseries.csv',parse_dates=['reporting_month'])
snap=pd.read_csv(ROOT/'data/reference/official_gateway_selected_provider_snapshot.csv')

fig,ax=plt.subplots(figsize=(12,6))
for entity,g in ts.groupby('entity'):
    g=g.sort_values('reporting_month')
    ax.plot(g['reporting_month'],g['within_18_weeks_pct'],marker='o',label=entity)
ax.set_title('Elective proportion waiting within 18 weeks — verified NHS England snapshot')
ax.set_ylabel('Percent')
ax.set_xlabel('Reporting month')
ax.legend(loc='best',fontsize=8)
ax.grid(True,alpha=0.2)
fig.autofmt_xdate()
fig.text(0.01,0.01,'Source: NHS England Public Data Gateway. Prototype scope: England + 3 providers, Aug 2025–Jul 2026.',fontsize=8)
fig.tight_layout(rect=(0,0.04,1,1))
fig.savefig(OUT/'executive_overview_mockup.svg')
plt.close(fig)

plot=snap.sort_values('within_18_weeks_pct').copy()
fig,ax=plt.subplots(figsize=(12,8))
ax.barh(plot['provider'],plot['within_18_weeks_pct'])
ax.axvline(65.4,linestyle='--',label='England 65.4%')
ax.set_title('Selected provider benchmark — within 18 weeks, July 2026')
ax.set_xlabel('Percent')
ax.legend()
ax.grid(True,axis='x',alpha=0.2)
fig.text(0.01,0.01,'Selected benchmark extract, not a representative sample. Source: NHS England Public Data Gateway.',fontsize=8)
fig.tight_layout(rect=(0,0.04,1,1))
fig.savefig(OUT/'provider_performance_mockup.svg')
plt.close(fig)
print('generated mockups')
