# -*- coding: utf-8 -*-

import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec        

fn = 'data/Weather_station_data/CR1000XSeries_Table2.dat'

data = pd.read_csv(fn, 
                   skiprows=1,
                   header=[0,1],
                   sep=',',
                   #dtype='float',
                   index_col=0, 
                   low_memory=False)
tz = 'Europe/Oslo' #existing timezones can be checked using pytz.all_timezones[::20]
data.index = pd.to_datetime(data.index).tz_localize(tz=tz, 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')
data.columns = data.columns.to_flat_index()
day='08'
date = '2023-05-{}'.format(day)
times = pd.date_range(start=date, freq='1min', periods=24*60, tz=tz)
# how to use data_range https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases

G = pd.to_numeric(data[('Global_Avg', 'W.m-2')][times])
D = pd.to_numeric(data[('Diffuse_Avg', 'W.m-2')][times])

D_SPN1 = pd.to_numeric(data[('Solar_Wm2_1_Avg', 'W/m²')][times])
G_SPN1 = pd.to_numeric(data[('Solar_Wm2_2_Avg', 'W/m²')][times])

#%%
plt.figure(figsize=(8, 6))
gs1 = gridspec.GridSpec(1, 1)
gs1.update(wspace=0.4, hspace=0.2)

ax1 = plt.subplot(gs1[0,0])
ax1.plot(G, linewidth=2, color='orange', label='Global')
ax1.plot(D, linewidth=2, color='gold', label='Diffuse')
ax1.plot(G_SPN1, linewidth=2, color='orange', linestyle='-', label='G_SPN1')
ax1.plot(D_SPN1, linewidth=2, color='gold', linestyle='-', label='B_SPN1')
ax1.set_ylabel('W/m2')
plt.setp(ax1.get_xticklabels(), ha="right", rotation=45)
# ax1.set_ylim([0,40])
ax1.grid('--')
ax1.legend()
plt.savefig('Figures/Global_Irradiance_{}.jpg'.format(day), dpi=300, bbox_inches='tight')

#%%
Cell_1_1 = pd.to_numeric(data[('CS325DM_Analog1_1_Avg', 'W/m²')][times])
Cell_1_2 = pd.to_numeric(data[('CS325DM_Analog1_2_Avg', 'W/m²')][times])
Cell_1_3 = pd.to_numeric(data[('CS325DM_Analog1_3_Avg', 'W/m²')][times])
Cell_1_4 = pd.to_numeric(data[('CS325DM_Analog1_4_Avg', 'W/m²')][times])

plt.figure(figsize=(8, 6))
gs1 = gridspec.GridSpec(1, 1)
gs1.update(wspace=0.4, hspace=0.2)

ax1 = plt.subplot(gs1[0,0])
ax1.plot(Cell_1_1, linewidth=2, color='green', label='Cell_1_1')
ax1.plot(Cell_1_2, linewidth=2, color='blue', label='Cell_1_2')
ax1.plot(Cell_1_3, linewidth=2, color='red', label='Cell_1_3')
ax1.plot(Cell_1_4, linewidth=2, color='orange', label='Cell_1_4')
ax1.set_ylabel('W/m2')
plt.setp(ax1.get_xticklabels(), ha="right", rotation=45)
# ax1.set_ylim([0,40])
ax1.grid('--')
ax1.legend()
plt.savefig('Figures/Reflerence_cells_{}.jpg'.format(day), dpi=300, bbox_inches='tight')


# #('CS325DM_Analog1_1_Avg', 'W/m²'),
# ('CS325DM_Analog2_1_Avg', 'DegC'),
# ('CS325DM_Analog1_1_Std', 'W/m²'),
# ('CS325DM_Analog2_1_Std', 'DegC'),
# #('CS325DM_Analog1_2_Avg', 'W/m²'),
# ('CS325DM_Analog2_2_Avg', 'DegC'),
# ('CS325DM_Analog1_2_Std', 'W/m²'),
# ('CS325DM_Analog2_2_Std', 'DegC'),
# #('CS325DM_Analog1_3_Avg', 'W/m²'),
# ('CS325DM_Analog2_3_Avg', 'DegC'),
# ('CS325DM_Analog1_3_Std', 'W/m²'),
# ('CS325DM_Analog2_3_Std', 'DegC'),
# #('CS325DM_Analog1_4_Avg', 'W/m²'),
# ('CS325DM_Analog2_4_Avg', 'DegC'),
# ('CS325DM_Analog1_4_Std', 'W/m²'),
# ('CS325DM_Analog2_4_Std', 'DegC'),