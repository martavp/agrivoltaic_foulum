# -*- coding: utf-8 -*-

import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec        

fn = 'data/Inverter_20230505000000_20230605235959.xlsx'

data = pd.read_excel(fn, sheet_name="5 minutes", index_col=3, 
                     header=0, skiprows=3).squeeze("columns")

tz = 'Europe/Oslo' #existing timezones can be checked using pytz.all_timezones[::20]
data.index = pd.to_datetime(data.index).tz_localize(tz=tz)
inv1=data[data['ManageObject']=='Logger-1/INV-1-TBF']
inv2=data[data['ManageObject']=='Logger-1/INV-2-VBF']

# date = '2023-05-27'
# times = pd.date_range(start=date, freq='1H', periods=24, tz=tz)


#%%
days = [8, 22, 23, 24, 25, 26, 27, 28,29]
for day in days:
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    gs1.update(wspace=0.4, hspace=0.2)

    ax1 = plt.subplot(gs1[0,0])
    ax1.plot(inv1['Total input power(kW)'], 
          linewidth=2, color='dodgerblue', label='tilted DC')
    ax1.plot(inv2['Total input power(kW)'], 
          linewidth=2, color='firebrick', label='vertical DC')
    
    ax1.plot(inv1['Active power(kW)'], 
          linewidth=2, alpha=0.5,
          color='dodgerblue', label='tilted AC')
    ax1.plot(inv2['Active power(kW)'], 
          linewidth=2, alpha=0.5, 
          color='firebrick', label='vertical AC')
    ax1.set_xlim([datetime.date(2023, 5, day), datetime.date(2023, 5, day+1)])
    ax1.set_ylabel('PV Production (kW)')
    plt.setp(ax1.get_xticklabels(), ha="right", rotation=45)
    ax1.set_ylim([0,40])
    ax1.grid('--')
    ax1.legend()
    plt.savefig('Figures/curtailment_1_2_{}.jpg'.format(day), dpi=300, bbox_inches='tight')
    
#%%%    
for day in days:
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    gs1.update(wspace=0.4, hspace=0.2)

    ax1 = plt.subplot(gs1[0,0])
    ax1.plot(inv1['Total input power(kW)'], 
          linewidth=2, color='dodgerblue', label='tilted')
    ax1.plot(inv2['Total input power(kW)'], 
          linewidth=2, color='firebrick', label='vertical')

    ax1.set_xlim([datetime.date(2023, 5, day), datetime.date(2023, 5, day+1)])
    ax1.set_ylabel('PV Production (kW)')
    plt.setp(ax1.get_xticklabels(), ha="right", rotation=45)
    ax1.set_ylim([0,40])
    ax1.grid('--')
    ax1.legend()
    plt.savefig('Figures/inverter_1_2_{}.jpg'.format(day), dpi=300, bbox_inches='tight')
        
#%%

for day in days:
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    gs1.update(wspace=0.4, hspace=0.2)

    ax1 = plt.subplot(gs1[0,0])
    ax1.plot(inv1['PV1 input voltage(V)'], 
          linewidth=2, label='PV1')
    ax1.plot(inv1['PV2 input voltage(V)'], 
          linewidth=2, label='PV2')
    ax1.plot(inv1['PV3 input voltage(V)'], 
          linewidth=2, label='PV3')
    ax1.plot(inv1['PV4 input voltage(V)'], 
          linewidth=2, label='PV4')

    ax1.set_xlim([datetime.date(2023, 5, day), datetime.date(2023, 5, day+1)])
    ax1.set_ylabel('input voltage (V)')
    plt.setp(ax1.get_xticklabels(), ha="right", rotation=45)
    #ax1.set_ylim([0,40])
    ax1.grid('--')
    ax1.legend()
    plt.savefig('Figures/voltage_inv1_1_2_3_4_{}.jpg'.format(day), dpi=300, bbox_inches='tight')

#%%

for day in days:
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    gs1.update(wspace=0.4, hspace=0.2)

    ax1 = plt.subplot(gs1[0,0])
    ax1.plot(inv2['PV1 input voltage(V)'], 
          linewidth=2, label='PV1')
    ax1.plot(inv2['PV2 input voltage(V)'], 
          linewidth=2, label='PV2')
    ax1.plot(inv2['PV3 input voltage(V)'], 
          linewidth=2, label='PV3')
    ax1.plot(inv2['PV4 input voltage(V)'], 
          linewidth=2, label='PV4')

    ax1.set_xlim([datetime.date(2023, 5, day), datetime.date(2023, 5, day+1)])
    ax1.set_ylabel('input voltage (V)')
    plt.setp(ax1.get_xticklabels(), ha="right", rotation=45)
    #ax1.set_ylim([0,40])
    ax1.grid('--')
    ax1.legend()
    plt.savefig('Figures/voltage_inv2_1_2_3_4_{}.jpg'.format(day), dpi=300, bbox_inches='tight')
#%%    
for day in days:
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    gs1.update(wspace=0.4, hspace=0.2)

    ax1 = plt.subplot(gs1[0,0])
    ax1.plot(inv2['PV1 input current(A)'], 
          linewidth=1, label='PV1')
    ax1.plot(inv2['PV2 input current(A)'], 
          linewidth=1, label='PV2')
    ax1.plot(inv2['PV3 input current(A)'], 
          linewidth=1, label='PV3')
    ax1.plot(inv2['PV4 input current(A)'], 
          linewidth=1, label='PV4')

    ax1.set_xlim([datetime.date(2023, 5, day), datetime.date(2023, 5, day+1)])
    ax1.set_ylabel('input current (A)')
    plt.setp(ax1.get_xticklabels(), ha="right", rotation=45)
    #ax1.set_ylim([0,40])
    ax1.grid('--')
    ax1.legend()
    plt.savefig('Figures/current_inv2_1_2_3_4_{}.jpg'.format(day), dpi=300, bbox_inches='tight')

#%%    
for day in days:
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    gs1.update(wspace=0.4, hspace=0.2)

    ax1 = plt.subplot(gs1[0,0])
    ax1.plot(inv1['PV1 input current(A)'], 
          linewidth=1, label='PV1')
    ax1.plot(inv1['PV2 input current(A)'], 
          linewidth=1, label='PV2')
    ax1.plot(inv1['PV3 input current(A)'], 
          linewidth=1, label='PV3')
    ax1.plot(inv1['PV4 input current(A)'], 
          linewidth=1, label='PV4')

    ax1.set_xlim([datetime.date(2023, 5, day), datetime.date(2023, 5, day+1)])
    ax1.set_ylabel('input current (A)')
    plt.setp(ax1.get_xticklabels(), ha="right", rotation=45)
    #ax1.set_ylim([0,40])
    ax1.grid('--')
    ax1.legend()
    plt.savefig('Figures/current_inv1_1_2_3_4_{}.jpg'.format(day), dpi=300, bbox_inches='tight')
    