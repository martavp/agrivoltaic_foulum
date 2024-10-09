# -*- coding: utf-8 -*-

import pandas as pd
import pvlib
from pvlib.bifacial.pvfactors import pvfactors_timeseries
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import warnings
import numpy as np
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
    # When modeling fixed-tilt arrays, set this value to be 90 degrees clockwise from surface_azimuth.
        
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

"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

DEFINE PARAMETERS FROM PILOT PLANT

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

# We retrieve the PV modules specifications from the database at 
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

###factor= (1/1000)*20*4 # 4 rows of 20 PV modules, W -> kW

#For the temperature parameters, we assume an open rack glass-glass configuration.
temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

# Folum, Denmark
lat, lon =  56.497, 9.584
altitude = 39
tz='UTC'
#We define the location, date, and time zone. 
location = pvlib.location.Location(lat, lon, tz=tz)

albedo = 0.2

# vertical installation
tilt_v = 90
orientation_v = -84
pvrow_height_v = module_width + 0.2 + 0.1 #20 cm from the ground, 20 cm gap in the middle
pvrow_width_v = module_width*2 + 0.2 + 0.2 #20 cm from the ground, 20 cm gap in the middle
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

PVLIB MODEL  - ANNUAL YIELD CALCULATION

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
gcrs = np.arange(0.15,0.65,0.05)
yield_v = pd.Series(index=gcrs, dtype='float64')

# vertical installation
for gcr_v in gcrs:    
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
    yield_v[gcr_v] = dc_power_v['p_mp'].sum()/P


# tilted installation

yield_t = pd.Series(index=gcrs, dtype='float64')

for gcr_t in gcrs: 
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

    yield_t[gcr_t] = dc_power_t['p_mp'].sum()/P


#%%
plt.figure(figsize=(24, 18))
gs1 = gridspec.GridSpec(2, 2)
gs1.update(wspace=0.2, hspace=0.35)
ax1 = plt.subplot(gs1[0,0]) 
color_t='dodgerblue'
color_v='darkorange'
system_losses=0.16

ax1.plot([module_width*2/x for x in yield_v.index],
         yield_v.values*(1-system_losses),
         color=color_v,
         label='vertical, model (TMY)')

ax1.plot([module_width*2/x for x in yield_t.index],
         yield_t.values*(1-system_losses),
         color=color_t,
         label='south-oriented, model (TMY)')

ax1.grid()
ax1.axvline(x=11,color='grey', linewidth=3, linestyle='--')
ax1.set_ylabel('Annual electricity generation (kWh/kW)')
ax1.set_xlabel('inter-row distance (m)')
ax1.legend(fontsize=22, bbox_to_anchor=(1.01, 0.9))

def gcr2pitch(x):
    return module_width*2/x


def pitch2gcr(x):
    return module_width*2/x


ax10 = ax1.secondary_xaxis('top', functions=(pitch2gcr, gcr2pitch))
ax10.set_xlabel('ground cover ratio (GCR)')

ax1 = plt.subplot(gs1[1,0]) 

ax1.plot([module_width*2/x for x in yield_v.index],
         100*(1-yield_v.values/yield_v.values[0]),
         color=color_v,
         label='vertical, model (TMY)')

ax1.plot([module_width*2/x for x in yield_t.index],
         100*(1-yield_t.values/yield_t.values[0]),
         color=color_t,
         label='south-oriented, model (TMY)')

ax1.grid()
ax1.axvline(x=11,color='grey', linewidth=3, linestyle='--')
ax1.set_ylabel('Shadow losses (%)')
ax1.set_xlabel('inter-row distance (m)')
ax1.legend(fontsize=22, bbox_to_anchor=(1.01, 0.9))
ax1.set_ylim([0,25])

ax10 = ax1.secondary_xaxis('top', functions=(pitch2gcr, gcr2pitch))
ax10.set_xlabel('ground cover ratio (GCR)')

plt.savefig('Figures/annual_yield_vs_GCR.jpg', 
                dpi=100, bbox_inches='tight')
