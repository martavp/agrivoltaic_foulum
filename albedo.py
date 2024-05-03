# -*- coding: utf-8 -*-

"""
Calculate ground reflectivity based on measurements from
pyranometers facing up and down

"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 


start_date =  '2022-12-01 00:00:00' # '2024-03-28 00:00:00'
end_date = '2024-05-01 23:55:00'    # '2024-04-10 23:55:00'
tz = 'UTC' 
time_index = pd.date_range(start=start_date, 
                               end=end_date, 
                               freq='5min',  
                               tz=tz)

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) #.tz_convert(tz=tz)

reflectivity = data['Albedometer (W.m-2)']/data['GHI (W.m-2)']
                     

#%%
plt.figure(figsize=(16, 8))
gs1 = gridspec.GridSpec(1, 1)
ax0 = plt.subplot(gs1[0,0:3]) 

ax0.plot(reflectivity, 
         alpha=0.05,
         color='green',
         marker='o',
         markersize=5,
         linewidth=0,
         label='ground reflectivity')

ax0.set_ylabel('Ground reflectivity')
ax0.grid('--')
ax0.set_ylim([0, 0.6])
ax0.set_xlim([time_index[0], time_index[-1]])
# ax0.legend(fontsize=14, bbox_to_anchor=(1.1, 0.4))

plt.savefig('Figures/reflectivity.jpg', dpi=300, bbox_inches='tight')