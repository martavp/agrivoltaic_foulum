# -*- coding: utf-8 -*-
"""

@author: marta.victoria.perez
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True)

import numpy as np


# Monthly energy (MWh): sum 5-min power readings × (5/60 h) / 1000
monthly = data[['INV-1-TBF Active power (kW)',
                'INV-2-VBF Active power (kW)']].resample('ME').sum() * (5/60) / 1000
monthly.index = monthly.index.strftime('%b %Y')

x = np.arange(len(monthly))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x - width/2, monthly['INV-1-TBF Active power (kW)'],
       width, label='INV-1-TBF (25° tilt)', color='#5FA1D8')
ax.bar(x + width/2, monthly['INV-2-VBF Active power (kW)'],
       width, label='INV-2-VBF (vertical west)', color='#B31F20')

ax.set_xlabel('Month')
ax.set_ylabel('AC energy generation (MWh)')
ax.set_xticks(x)
ax.set_xticklabels(monthly.index, rotation=45, ha='right')
# Load PVGIS time series (1 kWp, Foulum coordinates)
def load_pvgis(path):
    df = pd.read_csv(path, skiprows=10, engine='python')
    df.index = pd.to_datetime(df['time'], format='%Y%m%d:%H%M', errors='coerce')
    df = df[df.index.notna()]
    return df['P'].astype(float)  # W per 1 kWp

pvgis_tbf      = load_pvgis('data/PVGIS/Timeseries_56.495_9.571_SA3_1kWp_crystSi_14_25deg_0deg_2005_2023.csv')
pvgis_vbf_west = load_pvgis('data/PVGIS/Timeseries_56.495_9.571_SA3_1kWp_crystSi_14_90deg_90deg_2005_2023.csv')
pvgis_vbf_east = load_pvgis('data/PVGIS/Timeseries_56.495_9.571_SA3_1kWp_crystSi_14_90deg_-90deg_2005_2023.csv')

# Average monthly energy per 1 kWp across TMY years (kWh)
def monthly_tmy(series):
    monthly_kwh = series.resample('ME').sum() / 1000
    return monthly_kwh.groupby(monthly_kwh.index.month).mean()

BIFACIALITY = 0.85

# Scale to 44.4 kWp, convert to MWh
tmy_tbf = monthly_tmy(pvgis_tbf) * 44.4 / 1000
# VBF: west-facing front + bifaciality × east-facing back
tmy_vbf = (monthly_tmy(pvgis_vbf_west) + BIFACIALITY * monthly_tmy(pvgis_vbf_east)) * 44.4 / 1000

# Map TMY calendar months to the actual x-axis positions
month_nums = pd.to_datetime(monthly.index, format='%b %Y').month

ax.plot(x, tmy_tbf.loc[month_nums].values, color='black', linewidth=2, marker='o',
        markerfacecolor='#5FA1D8', markeredgecolor='black', markersize=7,
        linestyle='--', label='Expected TMY (25° tilt)')
ax.plot(x, tmy_vbf.loc[month_nums].values, color='black', linewidth=2, marker='o',
        markerfacecolor='#B31F20', markeredgecolor='black', markersize=7,
        linestyle='--', label='Expected TMY (vertical, bifacial)')
ax.legend()
ax.grid(axis='y', linestyle='--')
fig.tight_layout()

fig.savefig('figures/performance_analysis.jpg',
                dpi=100, bbox_inches='tight')
plt.close(fig)





   