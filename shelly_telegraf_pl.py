#!/usr/bin/env /usr/bin/python3.9

#Get solar energy forecast from www.bcdcenergia.fi and outputs it in format readable by Telegraf
# Called few times a day (plus in startup) from Telegraf, results are resent to Powerguru and InfluDb


import json
import settings as s
from datetime import datetime

# Telegraf plugin
from typing import Dict
from telegraf_pyplug.main import print_influxdb_format


arska_settings = s.read_settings(s.arska_file_name)
shelly_url = arska_settings["shelly_url"]




def read_shelly():
    import requests
    url = shelly_url 
    r = requests.get(url)
    
    meter_data = json.loads(r.text)
    meter_id = meter_data["mac"]
    power = 0
    current = 0
    total_energy = 0
    total_returned_energy =0

    for meter in meter_data["emeters"]:
        power = power + meter["power"]
        current = current + meter["current"]
        total_energy = total_energy + meter["total"]
        total_returned_energy = total_returned_energy + meter["total_returned"]
  
    timestamp_nano =meter_data["unixtime"] *1000000000 

    METRIC_FIELDS: Dict[str, int] = {"power":power,"current":current}
    print_influxdb_format( measurement="energy", 
    tags = { "meterid": meter_id,  "name" : "Shelly"},
    fields=METRIC_FIELDS,
    nano_timestamp=timestamp_nano)


read_shelly()		


