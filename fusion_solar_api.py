# -*- coding: utf-8 -*-

from fusion_solar_py.client import FusionSolarClient

# log into the API 
client = FusionSolarClient("aarhusuniversity", 
                           "hyperfarm2019",
                           huawei_subdomain="region02eu5")

# get the stats
stats = client.get_power_status()

# print all stats
print(f"Current power: {stats.current_power_kw} kW")
print(f"Total energy today: {stats.energy_today_kwh} kWh")
print(f"Total energy: {stats.energy_kwh} kWh")
#%%
# log out - just in case
client.log_out()

#%%

# if you only need an overview of the current status of
# your plant(s) you can use the get_plant_list function
plant_overview = client.get_station_list()

# get the current power of your first plant
print(f"Current power production: { plant_overview[0]['currentPowwer'] }")

#%%
# alternatively, you can get time resolved data for each plant:

# get the plant ids
plant_ids = client.get_plant_ids()

print(f"Found {len(plant_ids)} plants")
#%%
# get the basic (current) overview data for the plant
plant_overview = client.get_current_plant_data(plant_ids[0])

print(str(plant_overview))

# get the data for the first plant
plant_data = client.get_plant_stats(plant_ids[0])

# plant_data is a dict that contains the complete
# usage statistics of the current day. There is
# a helper function available to extract some
# most recent measurements
last_values = client.get_last_plant_data(plant_data)

print(f"Last production at {last_values['productPower']['time']}: {last_values['productPower']['value']}")

# In case you have a battery installed
print(f"Last battery charge at {last_values['chargePower']['time']}: {last_values['chargePower']['value']}")

# Additionally, if you have a meter installed you can get additional statistics
print(f"Total power consumption (today): {last_values['totalUsePower']} kWh")
print(f"Total produced power (today): {last_values['totalPower']} kWh")
print(f"Produced power consumed (today): {last_values['totalSelfUsePower']} kWh")
print(f"Relative amount of used power bought from grid: {last_values['buyPowerRatio']}%")

# print all optimizer stats
for x in client.get_optimizer_stats(client.get_device_ids()['Inverter']):
    print(f"{x['optName']}: {x['moStatus']} {x['runningStatus']}: {x['outputPower']} W /" +
          f" {x['inputVoltage']} V / {x['inputCurrent']} A / {x['temperature']} C")


# log out - just in case
client.log_out()

object_methods = [method_name for method_name in dir(client)
                  if callable(getattr(client, method_name))]

client.get_device_ids()
client.get_current_plant_data('NE=130060638')