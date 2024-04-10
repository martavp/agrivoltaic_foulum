# -*- coding: utf-8 -*-
"""
TODOs
1. Cambiar modelo de bifacial vertical (ahora suma la irradiancia de dos 
paneles mirando al E y W) por un modelo real de bifacial. 
2. Poner los datos reales del nuestros paneles fotovoltaicos

"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 
import matplotlib.dates as mdates
import pvlib

plt.style.use(['seaborn-ticks','pv-textbook.mplstyle'])

"""

PVLIB MODEL  - MONTHLY VALUES

tilt installation: orientation: 184, (tilt=25)
vertical installation: 97, 

"""

# Folum, Denmark
lat, lon =  56.497, 9.584
altitude = 39
tz = 'UTC'

#We start by defining the location, date, and time zone. 
location = pvlib.location.Location(lat, lon, tz=tz)

# We retrieve typical meteorological year (TMY) data from PVGIS.
tmy, _, _, _ = pvlib.iotools.get_pvgis_tmy(latitude=lat, 
                                           longitude=lon, 
                                           map_variables=True)

tmy.index = tmy.index.tz_convert(tz) # use local time

# We retrieve the PV modules and inverter specifications from the database at 
# the NREL SAM (System Advisory Monitoring).
# TODO: include real PV modules data
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod') 
module = sandia_modules['LG_LG290N1C_G3__2013_'] # module LG290N1C

#bifaciality coefficient
bifaciality = 0.8


#For the temperature parameters, we assume an open rack glass-glass configuration.
temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']


def calculate_irradiance_poa2(tilt, orientation, tmy):    
    
    """
    Calculate irradiance and effective irradiance on plane of array (POA)
    for a full TMY

    """
    # calculate Sun's coordinates
    solar_position = location.get_solarposition(times=tmy.index)
    
    #calculate airmass 
    airmass = pvlib.atmosphere.get_relative_airmass(solar_position['apparent_zenith'])
    pressure = pvlib.atmosphere.alt2pres(altitude)
    am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
    
    poa_irradiance = pvlib.irradiance.get_total_irradiance(surface_tilt=tilt,
                                                           surface_azimuth=orientation,
                                                           dni=tmy['dni'],
                                                           ghi=tmy['ghi'],                                                            
                                                           dhi=tmy['dhi'],
                                                           solar_zenith=solar_position['apparent_zenith'],
                                                           solar_azimuth=solar_position['azimuth'])
    #calculate the angle of incidence (aoi)
    aoi = pvlib.irradiance.aoi(surface_tilt=tilt,
                               surface_azimuth=orientation,                              
                               solar_zenith=solar_position['apparent_zenith'],
                               solar_azimuth=solar_position['azimuth'])

    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(poa_irradiance['poa_direct'],
                                                                    poa_irradiance['poa_diffuse'],
                                                                    am_abs,
                                                                    aoi,
                                                                    module)

    return poa_irradiance['poa_global'], effective_irradiance


poa_up, effective_up = calculate_irradiance_poa2(25,184, tmy)
poa_down, effective_down = calculate_irradiance_poa2(155,184, tmy)
cell_temperature_t = pvlib.temperature.sapm_cell(poa_up+bifaciality*poa_down,
                                                 tmy["temp_air"],
                                                 tmy["wind_speed"],
                                                 **temperature_model_parameters,)
dc_power_t = pvlib.pvsystem.sapm(effective_up+bifaciality*effective_down, 
                                 cell_temperature_t, 
                                 module)

poa_west, effective_west = calculate_irradiance_poa2(90,-84, tmy)
poa_east, effective_east = calculate_irradiance_poa2(90,96, tmy)
cell_temperature_v = pvlib.temperature.sapm_cell(poa_west+bifaciality*poa_east,
                                                 tmy["temp_air"],
                                                 tmy["wind_speed"],
                                                 **temperature_model_parameters,)
dc_power_v = pvlib.pvsystem.sapm(effective_west+bifaciality*effective_east, 
                                 cell_temperature_v, 
                                 module)

    
dc_power_v_m = dc_power_v['p_mp'].groupby(dc_power_v['p_mp'].index.month).sum().reset_index()
dc_power_t_m = dc_power_t['p_mp'].groupby(dc_power_t['p_mp'].index.month).sum().reset_index()


plt.figure(figsize=(16, 12))
gs1 = gridspec.GridSpec(2, 2)

ax1 = plt.subplot(gs1[0,1])
color1 ='dodgerblue',
color2='darkorange'
factor= (1/1000)*555/290*20*4 # 4 rows of 20 PV modules of 555 W, instead of 290, W -> kW
ax1.bar(dc_power_t_m['time(UTC)']-0.3,
        0.001*factor*dc_power_t_m['p_mp'], #kW to MW
        width=0.2,
        color='white',
        edgecolor=color1, #'black'
        label='tilted model (TMY)')
ax1.bar(dc_power_v_m['time(UTC)']+0.1,
        0.001*factor*dc_power_v_m['p_mp'],
        width=0.2,
        color='white',
        edgecolor=color2, #dimgray
        label='vertical model (TMY)')
ax1.set_xticks(dc_power_v_m['time(UTC)'])
ax1.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
ax1.set_ylabel('DC energy (MWh)')

ax1.text(0.05, 0.95, 'b)', 
         fontsize=20,
         horizontalalignment='center',
         verticalalignment='center', 
         transform=ax1.transAxes)

#sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
#inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_'] # inverter ABB-MICRO-0.25


#%%
"""

MEASURED DATA - DAILY VALUES

"""
data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 

day='2023-05-12 00:00:00+00:00'

ax0 = plt.subplot(gs1[0,0])
time_index = pd.date_range(start=day, 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)
#power generation inverter   
ax0.plot(data['INV-1-TBF Total input power (kW)'][time_index], 
              color='dodgerblue',
              label='tilted measured power')

ax0.plot(data['INV-2-VBF Total input power (kW)'][time_index], 
              color='darkorange',
              label='vertical measured power')

ax0.set_ylim([0,40])
ax0.set_ylabel('DC Power (kW)')
ax0.xaxis.set_major_formatter(mdates.DateFormatter('%H:%m'))
ax0.set_xlim([time_index[24], time_index[264]])
plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
ax0.grid('--')
ax0.text(0.05, 0.95, 'a)', 
         fontsize=20,
         horizontalalignment='center',
         verticalalignment='center', 
         transform=ax0.transAxes)
#%%%
"""

PVLIB - Model dc power on one day

"""
ghi = data['GHI_SPN1 (W.m-2)'][time_index]  # 'GHI (W.m-2)'
dhi = data['DHI_SPN1 (W.m-2)'][time_index] 
wind_speed = data['wind velocity (m.s-1)'][time_index]

# use 2nd weather station since ambient temperature not properly measured in the first station
# interpolate since only hourly data is available
temp_air = data['Ambient Temperature_2nd station (Deg C)'][time_index].interpolate()

solar_position = location.get_solarposition(times=time_index)

dni = pvlib.irradiance.dni(ghi, 
                           dhi, 
                           solar_position['apparent_zenith'], 
                           clearsky_dni=None, 
                           clearsky_tolerance=1.1, 
                           zenith_threshold_for_zero_dni=88.0, 
                           zenith_threshold_for_clearsky_limit=80.0)
#tilted array                           
airmass = pvlib.atmosphere.get_relative_airmass(solar_position['apparent_zenith'])
pressure = pvlib.atmosphere.alt2pres(altitude)
am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)


def calculate_irradiance_poa(tilt, orientation):
    """
    Calculate irradiance and effective irradiance on plane of array (POA)
    using measured weather data

    """
    
    poa_irradiance = pvlib.irradiance.get_total_irradiance(surface_tilt=tilt,
                                                           surface_azimuth=orientation,
                                                           dni=dni,
                                                           ghi=ghi,
                                                           dhi=dhi,
                                                           solar_zenith=solar_position['apparent_zenith'],
                                                           solar_azimuth=solar_position['azimuth'])
    
    #calculate the angle of incidence (aoi)
    aoi = pvlib.irradiance.aoi(surface_tilt=tilt,
                               surface_azimuth=orientation,                              
                               solar_zenith=solar_position['apparent_zenith'],
                               solar_azimuth=solar_position['azimuth'])

    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(poa_irradiance['poa_direct'],
                                                                    poa_irradiance['poa_diffuse'],
                                                                    am_abs,
                                                                    aoi,
                                                                    module)

    return poa_irradiance['poa_global'], effective_irradiance

poa_west, effective_west=calculate_irradiance_poa(90,-84)
poa_east, effective_east=calculate_irradiance_poa(90,96)

# calculate the solar cell temperature
cell_temperature_v = pvlib.temperature.sapm_cell(poa_west+bifaciality*poa_east,
                                                 temp_air,
                                                 wind_speed,
                                                 **temperature_model_parameters,)
#calculate the DC generation in every hour

dc_power_v = factor*pvlib.pvsystem.sapm(effective_west+bifaciality*effective_east, 
                                         cell_temperature_v, 
                                         module)
ax0.plot(dc_power_v['p_mp'], 
          color='darkorange',
          linestyle='--',
          label='vertical modeled power')
#%%
#tilted array                           
poa_up, effective_up=calculate_irradiance_poa(25,184)
poa_down, effective_down=calculate_irradiance_poa(155,184)

cell_temperature_t = pvlib.temperature.sapm_cell(poa_up+bifaciality*poa_down,
                                                    temp_air,
                                                    wind_speed,
                                                    **temperature_model_parameters,)

dc_power_t = factor*pvlib.pvsystem.sapm(effective_up+bifaciality*effective_down, 
                                         cell_temperature_t, 
                                         module)

ax0.plot(dc_power_t['p_mp'], 
         color='dodgerblue',
         linestyle='--',
         label='tilted modeled power')

#%%%
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
                  alpha=0.7)
ax01.set_ylim([2500,6000])
ax0.xaxis.set_major_formatter(mdates.DateFormatter('%H:%m'))

#%%%
"""

MEASURED POWER GENERATION - MONTHLY DATA

"""
factor2 = (1/1000)*(1/12) #5 minutes resolution, kW -> MW  
dc_energy_t_m = data['INV-1-TBF Total input power (kW)'].groupby(data['INV-1-TBF Total input power (kW)'].index.month).sum().reset_index()
dc_energy_v_m =data['INV-2-VBF Total input power (kW)'].groupby(data['INV-1-TBF Total input power (kW)'].index.month).sum().reset_index()

ax1.bar(dc_energy_t_m['index']-0.1,
        factor2*dc_energy_t_m['INV-1-TBF Total input power (kW)'],
        width=0.2,
        color=color1,
        label='tilted measured')

ax1.bar(dc_energy_v_m['index']+0.3,
        factor2*dc_energy_v_m['INV-2-VBF Total input power (kW)'],
        width=0.2,
        color=color2,
        label='vertical measured')
ax1.yaxis.grid('--')
ax1.set_ylim([0,9])
ax1.legend(fontsize=14, bbox_to_anchor=(1.01, 0.3))


ax2 = plt.subplot(gs1[1,0])
ax2.text(0.05, 0.95, 'c)', 
         fontsize=20,
         horizontalalignment='center',
         verticalalignment='center', 
         transform=ax2.transAxes)
"""

Subfigure C

"""
ax3 = plt.subplot(gs1[1,1])
#power generation per string 
colors=['firebrick', 'green', 'orange', 'gold']
for i in ['1', '2', '3', '4']:
    ax3.plot(0.001*data['VBF PV{} input voltage (V)'.format(i)][time_index]*data['VBF PV{} input current (A)'.format(i)][time_index], 
             color=colors[int(i)-1],
             alpha=0.8,
             label='vertical row {}'.format(i))
 
ax3.set_ylim([0,10])
ax3.set_xlim(time_index[0], time_index[-1])
ax3.set_ylabel('DC Power (kW)')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%m'))
ax3.set_xlim([time_index[24], time_index[264]])
plt.setp(ax3.get_xticklabels(), ha="right", rotation=45)
ax3.grid('--')
ax3.legend(fontsize=14, bbox_to_anchor=(1.01, 0.3))

 
ax3.text(0.05, 0.95, 'd)', 
         fontsize=20,
         horizontalalignment='center',
         verticalalignment='center', 
         transform=ax3.transAxes)

plt.savefig('Figures/figure_paper.jpg', 
                dpi=100, bbox_inches='tight')
    
