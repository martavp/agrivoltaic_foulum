# -*- coding: utf-8 -*-

"""
Calculate efficiency for both systems

"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 
date ='2024-09-19 '
start_date = date +'00:00:00' #day to be ploted
tz = 'UCT' 
start_t = date + '05:30:00' 
end_t = date + '09:00:00' 

start_t2 = date + '14:00:00' 
end_t2 = date + '16:00:00' 

start_v = date + '13:30:00' 
end_v = date + '17:00:00' 

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 


time_index_day = pd.date_range(start=start_date, 
                           periods=24*1*12, 
                           freq='5min',
                           tz=tz)

area = 80*2.280*1.134 #80 PV panels per inverter
bifaciality=0.8

irradiance_tilted = (data['Reference Cell Tilted facing up (W.m-2)'] +
                     bifaciality*data['Reference Cell Tilted facing down (W.m-2)'])

irradiance_vertical = (bifaciality*data['Reference Cell Vertical East (W.m-2)']
                       + data['Reference Cell Vertical West (W.m-2)'])

data['Efficiency INV-1-TBF'] = (1000/area)* data['INV-1-TBF Total input power (kW)'] / irradiance_tilted

data['Efficiency INV-2-VBF'] = (1000/area)* data['INV-2-VBF Total input power (kW)'] / irradiance_vertical

#%%
plt.figure(figsize=(18, 30))
gs1 = gridspec.GridSpec(5, 5)
gs1.update(wspace=0.2, hspace=0.2)
ax0 = plt.subplot(gs1[0,0:3]) 
ax1 = plt.subplot(gs1[1,0:3]) 
ax2 = ax1.twinx()
ax3 = plt.subplot(gs1[2,0:3]) 
ax4 = ax3.twinx()
ax5 = plt.subplot(gs1[3,0:3]) 
color_v = 'darkorange'
color_t = 'dodgerblue'

ax0.plot(data['Efficiency INV-1-TBF'][time_index_day], 
         alpha=0.5,
         color=color_t,
         marker='o',
         markersize=5,
         linewidth=0,
         label='Efficiency INV-1-TBF')
ax0.plot(data['Efficiency INV-2-VBF'][time_index_day], 
         alpha=0.5,
         color=color_v,
         marker='o',
         markersize=5,
         linewidth=0,
         label='Efficiency INV-2-VBF')
ax0.set_ylabel('Efficiency')
ax0.grid('--')
ax0.set_ylim([0.07, 0.22])
ax0.set_xlim([time_index_day[0], time_index_day[-1]])
ax0.legend(fontsize=14, bbox_to_anchor=(1.1, 0.4))
ax0.axvspan(start_t, end_t, facecolor='grey', alpha=0.2)
ax0.axvspan(start_t2, end_t2, facecolor='grey', alpha=0.2)
ax0.axvspan(start_v, end_v, facecolor='green', alpha=0.1)

sources = [ 'INV-1-TBF Total input power (kW)',
          'INV-2-VBF Total input power (kW)']

sources_r = ['Reference Cell Tilted facing up (W.m-2)',
           'Reference Cell Tilted facing down (W.m-2)',
           'GHI (W.m-2)',
           'Reference Cell Vertical East (W.m-2)',
           'Reference Cell Vertical West (W.m-2)']
colors=['black', 'green', 'red']

for i, source in enumerate(sources[0:1]):
    ax1.plot(data[source][time_index_day], 
             alpha=0.5,
             color=colors[i],
             label=source)
    ax1.legend(fontsize=14, bbox_to_anchor=(1.1, 0.5))
ax1.axvspan(start_t, end_t, facecolor='grey', alpha=0.2)
ax1.axvspan(start_t2, end_t2, facecolor='grey', alpha=0.2)
for i, source in enumerate(sources_r[0:2]):
    ax2.plot(data[source][time_index_day], 
             alpha=0.5,
             label=source)
    ax2.legend(fontsize=14, bbox_to_anchor=(1.1, 0.4))

for i, source in enumerate(sources[1:2]):
    ax3.plot(data[source][time_index_day], 
             alpha=0.5,
             color=colors[i],
             label=source)
    ax3.legend(fontsize=14, bbox_to_anchor=(1.1, 0.5))
ax3.axvspan(start_v, end_v, facecolor='green', alpha=0.1)    

for i, source in enumerate(sources_r[2:5]):
    ax4.plot(data[source][time_index_day], 
             alpha=0.5,
             label=source)
    ax4.legend(fontsize=14, bbox_to_anchor=(1.1, 0.4))     
    
ax1.set_ylabel('DC Power (kW)')    
ax2.set_ylabel('POA irradiance (W.m-2)') 
ax3.set_ylabel('DC Power (kW)')    
ax4.set_ylabel('POA irradiance (W.m-2)') 
ax1.set_xlim([time_index_day[0], time_index_day[-1]])
ax2.set_xlim([time_index_day[0], time_index_day[-1]])
ax3.set_xlim([time_index_day[0], time_index_day[-1]])
ax4.set_xlim([time_index_day[0], time_index_day[-1]])

time_index_t = pd.date_range(start=start_t, 
                               end=end_t, 
                               freq='5min',  
                               tz=tz)

time_index_t2 = pd.date_range(start=start_t2, 
                               end=end_t2, 
                               freq='5min',  
                               tz=tz)

time_index_v = pd.date_range(start=start_v, 
                               end=end_v, 
                               freq='5min',  
                               tz=tz)

# ax5.scatter(data['Reference Cell Tilted facing up (W.m-2)'][time_index_t],  
#             data['Efficiency INV-1-TBF'][time_index_t],  
#             color=color_t,
#             marker='s',
#             label='Efficiency INV-1-TBF')

ax5.scatter(data['Reference Cell Tilted facing up (W.m-2)'][time_index_t2],  
            data['Efficiency INV-1-TBF'][time_index_t2],  
            color=color_t,
            label='Efficiency INV-1-TBF')

ax5.scatter(data['Reference Cell Vertical West (W.m-2)'][time_index_v],  
            data['Efficiency INV-2-VBF'][time_index_v],  
            color=color_v,
            label='Efficiency INV-2-VBF')

ax5.set_ylabel('Efficiency')
ax5.set_xlabel('Front Plan of Array (POA) irradiance')
ax5.grid('--')
ax5.set_ylim([0.15, 0.20])
ax5.legend(fontsize=14, bbox_to_anchor=(1.4, 0.4))

plt.savefig('Figures/efficiency_analysis/Efficiency_analysis_{}.jpg'.format(date), dpi=300, bbox_inches='tight')

#%%
plt.figure(figsize=(6, 6))
gs1 = gridspec.GridSpec(1, 1)
ax0 = plt.subplot(gs1[0,0])
i=0
for i in range(1,5):
    ax0.scatter(data['TBF PV{} input current (A)'.format(str(i))][time_index_t2],  
                data['TBF PV{} input voltage (V)'.format(str(i))][time_index_t2],  
                marker='o',
                color='pink',
                alpha=0.5,
                label='tilted row {}'.format(str(i)))
    
    ax0.scatter(data['VBF PV{} input current (A)'.format(str(i))][time_index_t2],  
                data['VBF PV{} input voltage (V)'.format(str(i))][time_index_t2],  
                color='green',
                marker='x',
                alpha=0.5,
                label='vertical row {}'.format(str(i)))
ax0.set_ylabel('voltage (V)')
ax0.set_xlabel('current (A)')
ax0.legend(fontsize=14, bbox_to_anchor=(1.4, 0.4))
plt.savefig('Figures/efficiency_analysis/voltage_current_{}.jpg'.format(date), dpi=300, bbox_inches='tight')
