# -*- coding: utf-8 -*-

"""
Plot wind rose before and after the sensor placement and for both weather 
stations

2023/09/06 The wind sensor position changed on 6th September 2023 
and it was rotated around 180 degrees.
"""
from windrose import WindroseAxes
from matplotlib import pyplot as plt
import pandas as pd

#read clean data
start_date = '2023-01-30 00:00:00'
end_date = '2023-12-31 23:55:00'
tz = 'UTC' 
time_index = pd.date_range(start=start_date, 
                           end=end_date, 
                           freq='5min',
                           tz=tz)

start_date_bef = '2023-01-30 00:00:00'
end_date_bef = '2023-09-06 23:55:00' 
time_index_bef = pd.date_range(start=start_date_bef, 
                           end=end_date_bef, 
                           freq='5min',
                           tz=tz)

start_date_aft = '2023-09-07 00:00:00'
end_date_aft = '2023-10-31 23:55:00' 
time_index_aft = pd.date_range(start=start_date_aft, 
                           end=end_date_aft, 
                           freq='5min',
                           tz=tz)

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 

ws_bef=data['wind velocity (m.s-1)'][time_index_bef]
wd_bef= data['wind direction (deg)'][time_index_bef] #+180 already added when cleaning data

ws_aft=data['wind velocity (m.s-1)'][time_index_aft]
wd_aft=data['wind direction (deg)'][time_index_aft]

ws_2nd_2=data['wind velocity_2nd station 2m height (m.s-1)'][time_index_aft]
wd_2nd_2=data['wind direction_2nd station 2m height (deg)'][time_index_aft]

ws_2nd_10=data['wind velocity_2nd station 10m height (m.s-1)'][time_index_aft]
wd_2nd_10=data['wind direction_2nd station 10m height (deg)'][time_index_aft]

fig=plt.figure()
rect=[0.1,0,0.4,0.4] 
wa=WindroseAxes(fig, rect)
fig.add_axes(wa)
wa.bar(wd_bef, ws_bef, normed=True, opening=0.8, edgecolor='white')
#wa.set_legend()

rect1=[0.5, 0, 0.4, 0.4]
wa1=WindroseAxes(fig, rect1)
fig.add_axes(wa1)
wa1.bar(wd_aft, ws_aft, normed=True, opening=0.8, edgecolor='white')

rect2=[0.9, 0, 0.4, 0.4]
wa2=WindroseAxes(fig, rect2)
fig.add_axes(wa2)
wa2.bar(wd_2nd_2, ws_2nd_2, normed=True, opening=0.8, edgecolor='white')

rect3=[1.3, 0, 0.4, 0.4]
wa3=WindroseAxes(fig, rect3)
fig.add_axes(wa3)
wa3.bar(wd_2nd_10, ws_2nd_10, normed=True, opening=0.8, edgecolor='white')

plt.savefig('Figures/windrose_analysis.jpg', dpi=300, bbox_inches='tight')