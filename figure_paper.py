# -*- coding: utf-8 -*-

import pandas as pd
import pvlib
from pvlib.bifacial.pvfactors import pvfactors_timeseries
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import numpy as np
import warnings
# supressing shapely warnings that occur on import of pvfactors
warnings.filterwarnings(action='ignore', module='pvfactors')
plt.style.use(['seaborn-ticks','pv-textbook.mplstyle']) 


def calculate_irradiance_bifacial(tilt, 
                                  orientation, 
                                  bifaciality, 
                                  time_index,
                                  dni,
                                  dhi,
                                  solar_azimuth,
                                  solar_zenith,
                                  pvrow_height, 
                                  pvrow_width, 
                                  albedo, 
                                  gcr):
    """
    Calculate irradiance and effective irradiance on both planes of array (POA)
    using measured weather data or TMY and the pvfactors engine for both front  
    and rear-side effective irradiance
    """
    
    surface_azimuth = orientation
    surface_tilt = tilt
    axis_azimuth = orientation+90
    # axis_azimuth (float) – Azimuth angle of the rotation axis of the PV modules, 
    # using pvlib’s convention (deg). This is supposed to be fixed for all timestamps.
    # When modeling fixed-tilt arrays, set this value to be 90 degrees clockwise 
    # from surface_azimuth.
        
    irrad = pvfactors_timeseries(solar_azimuth,
                                 solar_zenith,
                                 surface_azimuth,
                                 surface_tilt,
                                 axis_azimuth,
                                 time_index,
                                 dni,
                                 dhi,
                                 gcr,
                                 pvrow_height,
                                 pvrow_width,
                                 albedo,
                                 n_pvrows=4,
                                 index_observed_pvrow=1)

    # turn into pandas DataFrame
    irrad = pd.concat(irrad, axis=1)

    # using bifaciality factor and pvfactors results, create effective irradiance
    effective_irrad_bifi = irrad['total_abs_front'] + (irrad['total_abs_back']
                                                       * bifaciality)
    return effective_irrad_bifi


plt.figure(figsize=(16, 12))
gs1 = gridspec.GridSpec(2, 2)
gs1.update(wspace=0.21, hspace=0.25)
ax0 = plt.subplot(gs1[0,1]) # daily generation
ax1 = plt.subplot(gs1[0,0]) # monthly generation
ax2 = plt.subplot(gs1[1,0]) # daily generation per string
ax3 = plt.subplot(gs1[1,1])
color_t='dodgerblue'
color_v='darkorange'


"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

1. LOAD MEASURED DATA AND PLOT DAILY GENERATION

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

#load measured data
data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 
tz='UTC'
day='2023-05-12 00:00:00+00:00'

time_index = pd.date_range(start=day, 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)
#power generation inverter   
ax0.plot(data['INV-2-VBF Total input power (kW)'][time_index]*(1/44.4), 
              color=color_v,
              label='vertical measured power')

ax0.plot(data['INV-1-TBF Total input power (kW)'][time_index]*(1/44.4), 
              color=color_t,
              label='tilted measured power')

ax0.set_ylim([0,1])
ax0.set_ylabel('DC Power (kW/kWp)')
ax0.xaxis.set_major_formatter(mdates.DateFormatter('%H:%m'))
ax0.set_xlim([time_index[24], time_index[264]])
plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
ax0.grid('--')
ax0.text(0.05, 0.95, 'b)', 
          fontsize=22,
          horizontalalignment='center',
          verticalalignment='center', 
          transform=ax0.transAxes)


"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

2. MEASURED POWER GENERATION - MONTHLY DATA

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

time_index_m = pd.date_range(start=day, 
                             periods=24*12*365, 
                             freq='5min',
                             tz=tz)
dc_energy_t_m = data['INV-1-TBF Total input power (kW)'][time_index_m].groupby(data['INV-1-TBF Total input power (kW)'][time_index_m].index.month).sum().reset_index()
dc_energy_v_m =data['INV-2-VBF Total input power (kW)'][time_index_m].groupby(data['INV-1-TBF Total input power (kW)'][time_index_m].index.month).sum().reset_index()

#estimate also annual GHI
GHI_SPN1_m = data['GHI_SPN1 (W.m-2)'][time_index_m].groupby(data['GHI_SPN1 (W.m-2)'][time_index_m].index.month).sum().reset_index()
GHI_m = data['GHI (W.m-2)'][time_index_m].groupby(data['GHI (W.m-2)'][time_index_m].index.month).sum().reset_index()

ax1.bar(dc_energy_t_m['index']-0.1,
        (1/12)*dc_energy_t_m['INV-1-TBF Total input power (kW)']*(1/44.4), #5 minutes resolution, kW -> kWh/kWp  
        width=0.2,
        color=color_t,
        label='tilted measured')

ax1.bar(dc_energy_v_m['index']+0.3,
        (1/12)*dc_energy_v_m['INV-2-VBF Total input power (kW)']*(1/44.4), #5 minutes resolution, kW -> kWh/kWp  
        width=0.2,
        color=color_v,
        label='vertical measured')
ax1.yaxis.grid('--')
ax1.set_ylim([0,200])


"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

DEFINE PARAMETERS FROM PILOT PLANT

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

# We retrieve the PV modules and inverter specifications from the database at 
# the NREL SAM (System Advisory Monitoring).
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod') 
module = sandia_modules['LG_LG290N1C_G3__2013_'] # module LG290N1C

# We define a new module based on Jolywood datasheet
Jolywood = module.copy() 
Jolywood['Vintage'] = 2023 
Jolywood['Area'] = 2.585      
Jolywood['Material'] = 'monoSi'  
Jolywood['Cells_in_Series'] =  144
Jolywood['Parallel_Strings'] = 2
Jolywood['Isco'] = 13.93     
Jolywood['Voco'] = 50.4       
Jolywood['Impo'] = 13.16     
Jolywood['Vmpo'] = 42.2    
Jolywood['Aisc'] = 0.00046                                                     
Jolywood['Aimp'] = 0.00046                                              
Jolywood['Bvoco'] = - 0.0026 * Jolywood['Voco']                                                       
Jolywood['Bvmpo'] =  - 0.0026 * Jolywood['Voco']           
Jolywood.name = "Jolywood_HD144N" 
module= Jolywood

P=Jolywood['Impo']*Jolywood['Vmpo'] #moduleo nominal capacity
module_length = 2.28
module_width = 1.1

bifaciality = 0.8

factor= (1/1000)*20*4 # 4 rows of 20 PV modules, W -> kW

#For the temperature parameters, we assume an open rack glass-glass configuration.
temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

# Folum, Denmark
lat, lon =  56.497, 9.584
altitude = 39
#We define the location, date, and time zone. 
location = pvlib.location.Location(lat, lon, tz=tz)

albedo = 0.2

# vertical installation
tilt_v = 90
orientation_v = -84
pvrow_height_v = module_width + 0.2 + 0.1 #50 cm from the ground, 20 cm gap in the middle
pvrow_width_v = module_width*2 + 0.2 + 0.2 #50 cm from the ground, 20 cm gap in the middle
pitch_v = 11
gcr_v=module_width*2/pitch_v

# tilted installation
tilt_t = 25
orientation_t = 184
pvrow_height_t=module_length/2*np.sin(25/180*np.pi) + 0.8 #80cm from the ground to the lowest point of the panel
pvrow_width_t = module_length
pitch_t = 12 
gcr_t=module_length/pitch_t

"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

3. PVLIB - DAILY GENERATION

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

day='2023-05-12 00:00:00+00:00'
time_index = pd.date_range(start=day, 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)
#measured GHI and DHI
ghi = data['GHI_SPN1 (W.m-2)'][time_index]  
dhi = data['DHI_SPN1 (W.m-2)'][time_index] 
wind_speed = data['wind velocity (m.s-1)'][time_index]

# use 2nd weather station since ambient temperature not properly measured in 
# the first station, interpolate since only hourly data is available
temp_air = data['Ambient Temperature_2nd station (Deg C)'][time_index].interpolate()

solar_position = location.get_solarposition(times=time_index)
solar_azimuth = solar_position['azimuth']
solar_zenith = solar_position['apparent_zenith']
#estimate dni from measured ghi and dhi
dni = pvlib.irradiance.dni(ghi, 
                           dhi, 
                           solar_zenith, 
                           clearsky_dni=None, 
                           clearsky_tolerance=1.1, 
                           zenith_threshold_for_zero_dni=88.0, 
                           zenith_threshold_for_clearsky_limit=80.0)
                          
airmass = pvlib.atmosphere.get_relative_airmass(solar_position['apparent_zenith'])
pressure = pvlib.atmosphere.alt2pres(altitude)
am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)


# total effective irradiance can be estimated using pvfactors irradiance model
# (function calculate_irradiance_bifacial)

# vertical installation
effective_irrad_bifi_v=calculate_irradiance_bifacial(tilt_v , 
                                                     orientation_v, 
                                                     bifaciality,
                                                     time_index,
                                                     dni,
                                                     dhi,
                                                     solar_azimuth,
                                                     solar_zenith,
                                                     pvrow_height_v, 
                                                     pvrow_width_v, 
                                                     albedo, 
                                                     gcr_v)

cell_temperature_v = pvlib.temperature.sapm_cell(effective_irrad_bifi_v,
                                                 temp_air,
                                                 wind_speed,
                                                 **temperature_model_parameters,)

dc_power_v = factor*pvlib.pvsystem.sapm(effective_irrad_bifi_v, 
                                         cell_temperature_v, 
                                         module)
ax0.plot(dc_power_v['p_mp']*(1/44.4), 
         color='orange',
         linestyle='--',
         label='vertical modeled power')

# tilted installation
effective_irrad_bifi_t=calculate_irradiance_bifacial(tilt_t, 
                                                     orientation_t,
                                                     bifaciality,
                                                     time_index,
                                                     dni,
                                                     dhi,
                                                     solar_azimuth,
                                                     solar_zenith,
                                                     pvrow_height_t, 
                                                     pvrow_width_t, 
                                                     albedo, 
                                                     gcr_t)

cell_temperature_t = pvlib.temperature.sapm_cell(effective_irrad_bifi_t,
                                                    temp_air,
                                                    wind_speed,
                                                    **temperature_model_parameters,)

dc_power_t = factor*pvlib.pvsystem.sapm(effective_irrad_bifi_t, 
                                         cell_temperature_t, 
                                         module)

ax0.plot(dc_power_t['p_mp']*(1/44.4), 
         color='dodgerblue',
         linestyle='--',
         label='tilted modeled power')
ax0.legend(fontsize=22, bbox_to_anchor=(1.01, 0.5))


"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

3. PVLIB MODEL  - MONTHLY VALUES

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

# We retrieve typical meteorological year (TMY) data from PVGIS.
tmy, _, _, _ = pvlib.iotools.get_pvgis_tmy(latitude=lat, 
                                           longitude=lon, 
                                           map_variables=True)

tmy.index = tmy.index.tz_convert(tz) # use local time
solar_position = location.get_solarposition(times=tmy.index)
solar_zenith = solar_position['apparent_zenith']
solar_azimuth = solar_position['azimuth']


# vertical installation
effective_irrad_bifi_v=calculate_irradiance_bifacial(tilt_v , 
                                                      orientation_v, 
                                                      bifaciality,
                                                      tmy.index,
                                                      tmy['dni'],
                                                      tmy['dhi'],
                                                      solar_azimuth,
                                                      solar_zenith,
                                                      pvrow_height_v, 
                                                      pvrow_width_v, 
                                                      albedo, 
                                                      gcr_v)

cell_temperature_v = pvlib.temperature.sapm_cell(effective_irrad_bifi_v,
                                                 tmy["temp_air"],
                                                 tmy["wind_speed"],
                                                 **temperature_model_parameters,)
dc_power_v = pvlib.pvsystem.sapm(effective_irrad_bifi_v, 
                                 cell_temperature_v, 
                                 module)

# tilted installation
effective_irrad_bifi_t=calculate_irradiance_bifacial(tilt_t , 
                                                      orientation_t, 
                                                      bifaciality,
                                                      tmy.index,
                                                      tmy['dni'],
                                                      tmy['dhi'],
                                                      solar_azimuth,
                                                      solar_zenith,
                                                      pvrow_height_t, 
                                                      pvrow_width_t, 
                                                      albedo, 
                                                      gcr_t)


cell_temperature_t = pvlib.temperature.sapm_cell(effective_irrad_bifi_t,
                                                 tmy["temp_air"],
                                                 tmy["wind_speed"],
                                                 **temperature_model_parameters,)
dc_power_t = pvlib.pvsystem.sapm(effective_irrad_bifi_t, 
                                 cell_temperature_t, 
                                 module)

dc_power_v_m = dc_power_v['p_mp'].groupby(dc_power_v['p_mp'].index.month).sum().reset_index()
dc_power_t_m = dc_power_t['p_mp'].groupby(dc_power_t['p_mp'].index.month).sum().reset_index()

system_losses=0.16

print("****** modelled yield tilted installation")
print(((1-system_losses)*factor*dc_power_t_m['p_mp'].sum()/44.4).round())
print("****** historial yield tilted installation")
print(((1/12)*dc_energy_t_m['INV-1-TBF Total input power (kW)'].sum()/44.4).round())
print("****** modelled annual GHI")
print((tmy['ghi'].sum()/1000).round())
print("****** historical annual GHI SPN1")
print((0.001*1/12*GHI_SPN1_m['GHI_SPN1 (W.m-2)'].sum()).round())
print("****** historical annual GHI")
print((0.001*1/12*GHI_m['GHI (W.m-2)'].sum()).round())

ax1.bar(dc_power_t_m['time(UTC)']-0.3,
        (1-system_losses)*factor*dc_power_t_m['p_mp']*(1/44.4), #kW to MW (to MWh/kW)
        width=0.2,
        color='white',
        edgecolor=color_t, 
        label='tilted model (TMY)')
ax1.bar(dc_power_v_m['time(UTC)']+0.1,
        (1-system_losses)*factor*dc_power_v_m['p_mp']*(1/44.4),
        width=0.2,
        color='white',
        edgecolor=color_v, 
        label='vertical model (TMY)')
ax1.set_xticks(dc_power_v_m['time(UTC)'])

ax1.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
ax1.set_ylabel('DC energy (kWh/kWp)')

ax1.text(0.05, 0.95, 'a)', 
          fontsize=22,
          horizontalalignment='center',
          verticalalignment='center', 
          transform=ax1.transAxes)
ax1.annotate('vertical measured',  fontsize=20, xy=(5, 4.5), xytext=(7.5, 147), color=color_v)
ax1.annotate('vertical modeled', fontsize=20, xy=(5, 4), xytext=(7.5, 135),  color=color_v)
ax1.annotate('tilted measured',  fontsize=20, xy=(5, 6), xytext=(7.5, 180), color=color_t)
ax1.annotate('tilted modeled', fontsize=20, xy=(5, 5.5), xytext=(7.5, 169),  color=color_t)

"""
Add electricity demand in Denmark in 2019
"""

#electricity demand in Denmark 2019
demand=pd.read_csv('data/electricity_demand_Denmark/time_series_60min_singleindex_filtered.csv',
                 index_col=0)

demand.index = pd.to_datetime(demand.index, utc=True) 

start_date='2019-01-01 00:00:00+00:00'
end_date='2019-12-31 00:00:00+00:00'

time_index_d = pd.date_range(start=start_date, 
                                     end=end_date, 
                                     freq='H',  
                                     tz=tz)

dem=demand['DK_load_actual_entsoe_transparency'][time_index_d]
hour = pd.to_timedelta(dem.index.hour, unit='H')
dem_day_mean = dem.groupby(hour).mean()
dem_day_sd = dem.groupby(hour).std()

ax01=ax0.twinx()
time_index_day = pd.date_range(start=day, 
                           periods=24, 
                           freq='H',
                           tz=tz)
ax01.fill_between(time_index_day, 
                  dem_day_mean-dem_day_sd, 
                  dem_day_mean+dem_day_sd,
                  color='dimgray',
                  alpha=0.2)
ax01.plot(time_index_day, 
                  dem_day_mean, 
                  color='dimgray',
                  alpha=0.7,
                  label='electricity demand')
ax01.set_ylim([2500,6000])
ax01.set_yticks([])
ax0.xaxis.set_major_formatter(mdates.DateFormatter('%H:%m'))
ax0.set_xlim([time_index[24], time_index[264]])
ax0.set_xticklabels([str(time_index[i].hour)+':00' for i in [24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264]])
ax01.legend(fontsize=22, bbox_to_anchor=(1.01, 0.6))

"""

%%%%%%%%%%%%%%%%%%%%%%
Subfigure C: Power generation per string
%%%%%%%%%%%%%%%%%%%%%%

"""

#power generation per string 
colors=['firebrick', 'green', 'orange', 'gold']
for i in ['1', '2', '3', '4']:
    ax3.plot(0.001*data['VBF PV{} input voltage (V)'.format(i)][time_index]*data['VBF PV{} input current (A)'.format(i)][time_index]*(1/11.1), 
             color=colors[int(i)-1],
             alpha=0.8,
             label='vertical row {}'.format(i))
 
ax3.set_ylim([0,0.9])
ax3.set_xlim(time_index[0], time_index[-1])
ax3.set_ylabel('DC Power (kW/kWp)')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%m'))
ax3.set_xlim([time_index[24], time_index[264]])
ax3.set_xticklabels([str(time_index[i].hour)+':00' for i in [24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264]])
plt.setp(ax3.get_xticklabels(), ha="right", rotation=45)
ax3.grid('--')
ax3.legend(fontsize=22, bbox_to_anchor=(1.01, 0.5))

 
ax3.text(0.05, 0.95, 'd)', 
         fontsize=22,
         horizontalalignment='center',
         verticalalignment='center', 
         transform=ax3.transAxes)


    
dc_power_v_m.sum()/dc_power_t_m.sum()

"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Efficiency calculation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
ax2.text(0.05, 0.95, 'c)', 
         fontsize=22,
         horizontalalignment='center',
         verticalalignment='center', 
         transform=ax2.transAxes)

tz = 'UCT' 
date = day[0:11]
start_t = date + '14:00:00' 
end_t = date + '16:00:00' 
time_index_t = pd.date_range(start=start_t, 
                               end=end_t, 
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



ax2.scatter(data['Reference Cell Tilted facing up (W.m-2)'][time_index_t],  
            data['Efficiency INV-1-TBF'][time_index_t],  
            color=color_t,
            label='Efficiency tilted')

ax2.scatter(data['Reference Cell Vertical West (W.m-2)'][time_index_t],  
            data['Efficiency INV-2-VBF'][time_index_t],  
            color=color_v,
            label='Efficiency vertical')

ax2.set_ylabel('Efficiency')
ax2.set_xlabel('Front Plan of Array (POA) irradiance')
ax2.grid('--')
ax2.set_ylim([0.16, 0.21])
ax2.legend(fontsize=22, loc='lower right') #, bbox_to_anchor=(1.4, 0.4))

plt.savefig('Figures/figure_paper.jpg', 
                dpi=100, bbox_inches='tight')