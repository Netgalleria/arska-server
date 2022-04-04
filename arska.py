#!/usr/bin/env /usr/bin/python3.9 
# coding: utf-8 
#from multiprocessing.dummy.connection import families
import traceback #error reporting
import sys
import json
import os
import signal


import settings as s #file names and functions shared with Telegraf plugins

import subprocess # for calling Telegraf command
import time
import pytz #time zone

from datetime import datetime

# Web server libraries
from aiohttp import web
from aiohttp.web import Response

from aiohttp_session import session_middleware  #pip3 install aiohttp_session[secure]
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_basicauth_middleware import basic_auth_middleware
import hashlib #  for optional web server authentication

from datetime import datetime
from threading import Thread


data_updates = {}

dayahead_list = None 
forecastpv_list = None
current_states = None
states = None
channels_list = None

# global variables
channels = []
sensorData = None

#init config class
arska = None   


def aggregate_dayahead_prices_timeser(start,end):
    global dayahead_list,  arska
    
    for time in range(start, end+1, arska.nettingPeriodMinutes*60):
        # Aggregate day-ahead prices
        energyPriceSpot = None
        if dayahead_list is not None:
            for price_entry in dayahead_list:
                if price_entry["timestamp"] <= time and  time< price_entry["timestamp"]+3600: # 60 minutesperiod
                    energyPriceSpot = price_entry["fields"]["energyPriceSpot"]
                    arska.set_variable_timeser("energyPriceSpot",time,round(energyPriceSpot,2))

        # now calculate spot price rank of current hour in different window sizes
        for bCode in arska.dayaheadWindowBlocks:
            rank = get_period_rank_timeser(time,bCode)
            if rank is not None:
                variable_code = arska.get_setting("spot_price_variable_code").format(bCode)
                arska.set_variable_timeser(variable_code,time,rank)


def aggregate_solar_forecast_timeser(start,end,location):
    global forecastpv_list, arska

    for time in range(start, end+1, arska.nettingPeriodMinutes*60):
        blockSums = {}
        for bCodei in arska.solarForecastBlocks:
            blockSums[str(bCodei)] = 0

        if forecastpv_list is not None:
            for fcst_entry in forecastpv_list:
                if location == fcst_entry["tags"]["location"]:
                    for bCodei in arska.solarForecastBlocks:
                        futureHours = bCodei        
                        if fcst_entry["timestamp"] < time+(futureHours*3600):
                            blockSums[str(bCodei)] += fcst_entry["fields"]["pvrefvalue"]

        for sfbCode,sfb in blockSums.items():  
            blockCode = arska.get_setting("solar_forecast_variable_code").format(sfbCode)
           # print(location, blockCode,time,round(sfb,2))
            arska.set_variable_timeser(blockCode,time,round(sfb,2))




class Arska:
    def __init__(self,init_file_name):
        self.settings = s.read_settings(init_file_name) 
        #add most important settings to attributes
        self.nettingPeriodMinutes = self.get_setting("nettingPeriodMinutes")
        self.dayaheadWindowBlocks = self.get_setting("dayaheadWindowBlocks") 
        self.solarForecastBlocks = self.get_setting("solarForecastBlocks") 

        self.bcdcLocationsHandled = self.get_setting("bcdcLocationsHandled")

        self.variables = {}
        self.variables_timeser = {}


    def get_current_period_start(self):
        return  int(time.time()/(self.nettingPeriodMinutes*60))*(self.nettingPeriodMinutes*60)

    # time series
    def set_variable_timeser(self,field_code,time,value,type = "num"):
        if field_code not in self.variables_timeser: # time series exists, use it
            self.variables_timeser[field_code] = {"values": {}, "type" : type}   
        self.variables_timeser[field_code]["values"][str(time)] = value


    def get_values_timeser(self,field_code,time_first=None, time_last=None,states_requested=None):
        if time_first is None:
            time_first = self.get_current_period_start()
        if time_last is None:
            time_last = time_first+24*3600-1
        if field_code not in self.variables_timeser:
            return {}

        return_values = {}
        for vkey,variable in self.variables_timeser[field_code]["values"].items():
            if str(time_first) <= vkey and vkey <= str(time_last):
                if states_requested is None:
                    return_values[vkey] = variable
                else: #state filter
                    var_out = []
                    for var in variable:
                        if var in states_requested:
                            var_out.append(var)
                       
                    return_values[vkey] = var_out
 
        return return_values


    def get_value_timeser(self,field_code,time,default_value = None):
        if field_code == 'mmdd' or field_code == 'hhmm':
            tz_local = pytz.timezone(arska.get_setting("timeZoneLocal"))
            dt = datetime.fromtimestamp(time, tz_local)
            if field_code == 'mmdd':
                return dt.strftime("'%m%d'")
            elif field_code == 'hhmm':
                return dt.strftime("'%H%M'")
        else:
            if field_code in self.variables_timeser:
                if str(time) in self.variables_timeser[field_code]["values"]:
                    if self.variables_timeser[field_code]["type"] == "str":
                        return "'{}'".format(self.variables[field_code]["values"][str(time)])
                    else:
                        return self.variables_timeser[field_code]["values"][str(time)]
                else:
                    return default_value
            else:
                return default_value



    def get_setting(self,field_code,default_value = None):
        if field_code in self.settings:
            return self.settings[field_code]
        else:
            return default_value

 

def sig_handler(signum, frame): # operations of exit
    pass
    exit(1)
    

def check_states_timeser(start, end):
    global states
    global arska
    print("aikaväli:",start, end)
    for time in range(start, end+1, arska.nettingPeriodMinutes*60):
        ok_states = []
        for state_key,state in states.items(): # check 
            if "enabledIf" in state:
                state_returned, error_in_test = test_formula_timeser( state["enabledIf"],time)  
                # do not replicate internal states, typically max 999
                if state_returned and not error_in_test and int(state_key)>arska.get_setting("states_internal_max"): 
                    ok_states.append(int(state_key))   #Voisi olla kai int tästä    

        #print (time, ok_states)
        arska.set_variable_timeser("states",time,ok_states,"list")

    return 


def test_formula_timeser(formula,time,debudError=False):
    global arska
    variable_keys = list(arska.variables_timeser.keys())

    variable_keys.append("hhmm")
    variable_keys.append("mmdd")
    eval_string = formula

    for vkey in variable_keys:
        if vkey in eval_string:
            variable_value = arska.get_value_timeser(vkey,time,None) ########
            if variable_value is not None:
                eval_string = eval_string.replace(vkey,str(variable_value))
            else:
                #print("test_formula_timeser: time {} Variable {} value was None:".format(time,vkey))
                return False, True
            
    try:
        eval_value = eval(eval_string,{})   
    except NameError:
        if debudError:
            print("Variable(s) undefined in " + eval_string)
        return False, True 

    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception( exc_type,exc_value, exc_traceback,limit=5, file=sys.stdout)
        print("eval_string: ",eval_string)
        return False, True  

    #print("formula {},  [{}] => {}".format(info,eval_string, eval_value))
    return eval_value, False 



def get_spot_sliding_window_periods(current_period_start_ts, window_duration_hours):
    # get entries from now to requested duration in the future, 
    # if not enough future exists, include periods from history to get full window size
    global dayahead_list
    if  dayahead_list is  None:
        return None

    # get max and min
    min_dayahead_time = current_period_start_ts +10*24*3600
    max_dayahead_time = 0
    for price_entry in dayahead_list:
        min_dayahead_time = min(min_dayahead_time,price_entry["timestamp"])
        max_dayahead_time = max(max_dayahead_time,price_entry["timestamp"])      


    window_end_excl = min(current_period_start_ts + window_duration_hours*3600,max_dayahead_time)
    window_start_incl = window_end_excl-window_duration_hours*3600


    entry_window = []
    for price_entry in dayahead_list:
        if window_start_incl <= price_entry["timestamp"]  and price_entry["timestamp"] < window_end_excl:
            tsstr = datetime.fromtimestamp(price_entry["timestamp"]).strftime("%Y-%m-%dT%H:%M") 
            entry_window.append({"ts":price_entry["timestamp"],"value":round(price_entry["fields"]["energyPriceSpot"],2), "tsstr":tsstr})
          
    entry_window_sorted = sorted(entry_window, key=lambda entry: entry["value"])
    return entry_window_sorted



def get_period_rank_timeser(time, window_duration_hours):
    global arska
    price_window_sorted = get_spot_sliding_window_periods(time, window_duration_hours)
    rank = 1
    if price_window_sorted is not None:
        for entry in price_window_sorted:
            if time == entry["ts"]:
                return rank
            rank += 1

    return None


def load_program_config():
    global arska
    global states 
    global dayahead_list, forecastpv_list
    
    arska = Arska(s.arska_file_name) 

    #TODO: read cached forecast and price info and check validity?
    # states
    states = s.read_settings(s.states_filename) 
    
    # TODO: cache expiration to parameters
    expire_file_cache_h = 8
    dayahead_list,dayahead_mtime = load_data_json(s.dayahead_file_name) 
    if dayahead_list is not None and time.time()-dayahead_mtime>expire_file_cache_h*3600:
        print("Cached {} to old {} hours.".format(s.dayahead_file_name,(time.time()-dayahead_mtime)/3600))
        dayahead_list = None
        
    forecastpv_list, forecastpv_mtime = load_data_json(s.forecastpv_file_name) 
    if forecastpv_list is not None and time.time()-forecastpv_mtime>expire_file_cache_h*3600:
        print("Cached {} to old {} hours.".format(s.forecastpv_file_name,(time.time()-forecastpv_mtime)/3600))
        forecastpv_list = None
    return None


def load_data_json(file_name):  
    if not os.path.exists(file_name):
        return None, None
    try:
        mtime = os.path.getmtime(file_name)
        with open(file_name) as json_file:
            return json.load(json_file),mtime
    except:
        return None, None


def save_data_json(field_list,file_name): 
    try:
        with open(file_name, 'w') as outfile:
            json.dump(field_list, outfile)
        return True
    except:
        return False


def filtered_fields(field_list,tag_name_value, save_file_name = ''):
    global data_updates
    tz_utc = pytz.timezone("UTC")
    
    latest_ts = 0
    
    result_set = []
    for field in field_list:
        if "tags" not in field:
            continue
        if "name" not in field["tags"]:
            continue
        if field["tags"]["name"]==tag_name_value:
            result_set.append(field)
            if "timestamp" in field:
                latest_ts = max(latest_ts,field["timestamp"] )

    if len(result_set)>0:
        print("{:s} , fields with tag name {:s} :".format(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), tag_name_value),end = ' ')        
        print(str(len(result_set)) + " rows received" )
            
        data_updates[tag_name_value] = {"updated" : tz_utc.localize(datetime.utcnow()), "latest_ts" : latest_ts }
 
    if len(result_set)>0 and save_file_name:
        save_data_json(result_set,save_file_name)
    
    return result_set



async def serve_states(request):
    # report in GitHub markdown format
    text_out = "| State      | Description  | Rule |\n|----------|--------- |----|\n" 
    for code, state in states.items():
        if "enabledIf" in state:
            code_str = str(code)
            enabledIf = state["enabledIf"]
        else:
            code_str = '**' + str(code) + '-** '
            enabledIf = ""
        text_out += "| {} | {} | {} |\n".format(code_str,state["desc"],enabledIf)

    return Response(text=text_out, content_type='text/plain')


def get_requested_states(request):
    if not 'states' in request.rel_url.query:
        print("Missing parameter: states")
        #return Response(text="Missing parameter: states", content_type='text/html')
        return None
    else:
        states_requested_str = request.rel_url.query['states']

    states_requested = states_requested_str.split(",")

    for idx, state in enumerate(states_requested):
        if state.strip().isdigit():
            states_requested[idx] = int(state.strip())
    return states_requested
  

async def serve_state_series(request):
    global arska
    #TODO: cache in the future
    #TODO: limit queries, eg. 4 for ip-address/24h if no API-key, with API key more but not unlimited

    #states_requested = get_requested_states(request) # return only requested states
    states_requested = None # return all valid states
    if not 'price_area' in request.rel_url.query:
        return Response(text="Missing parameter: price_area", content_type='text/html')

    if not 'location' in request.rel_url.query:
        return Response(text="Missing parameter: location", content_type='text/html')
        

    if not 'api_key' in request.rel_url.query:
        return Response(text="Missing parameter: api_key", content_type='text/html')
    elif request.rel_url.query['api_key'] not in arska.get_setting("client_api_keys"):
        return Response(text="Invalid api_key", content_type='text/html')
    
    #TODO: nämä parametreista
    start = arska.get_current_period_start()
    end = start +3600*24
    location = request.rel_url.query['location']

    # user can limit the time window, in future cached version there could be cache filters
    if 'start' in request.rel_url.query:
        start = max(start,int(request.rel_url.query['start']))
    if 'end' in request.rel_url.query:
        end = min(end,int(request.rel_url.query['end']))

    #One instance supports only one price area
    price_area = request.rel_url.query['price_area']
    if price_area != arska.get_setting("SpotPriceArea"):
        return Response(text="Only price_area {} is supported by this server.".format(arska.get_setting("SpotPriceArea")), content_type='text/html')

    #first create time series for variables (excluding internal)
    aggregate_dayahead_prices_timeser(start,end)
    aggregate_solar_forecast_timeser(start,end,location)

    # this populates states timeseries
    check_states_timeser(start,end)

    state_series = arska.get_values_timeser("states",start,end,states_requested)
    state_series["ts"] = time.time()
    state_series["expires"] = int(time.time()) + arska.get_setting("state_series_ttl",7200)
    state_series["node_priority"] = 0


    return Response(text=json.dumps(state_series), content_type='application/json')
    

#handle http data from Telegraf 
async def process_telegraf_post(request):
    global dayahead_list, forecastpv_list
    global arska
    obj = await request.json()
    #TODO: different metrics could be parametrized, so addional metrics (eg. PV inverter data) could be added without code changes
    if "metrics" in obj:
        dayahead_new = filtered_fields(obj["metrics"],"dayahead",s.dayahead_file_name)
        if len(dayahead_new)>0:
            dayahead_list = dayahead_new
          
        forecastpv_new = filtered_fields(obj["metrics"],"forecastpv",s.forecastpv_file_name)
        if len(forecastpv_new)>0:
            forecastpv_list = forecastpv_new

    return web.Response(text=f"Thanks for your contibution Telegraf!")

       
#run Telegraf on startup  
def run_telegraf_once(cmd = None, start_delay = 10):  
    if cmd is None:
        cmd = arska.get_setting("telegraf_once_cmd")
    try:
        time.sleep(start_delay) # let the main thread start
        cmd_arr = cmd.split()
        FNULL = open(os.devnull, 'w') 
        telegrafProcess = subprocess.Popen(cmd_arr, shell=False,stdout=FNULL, stderr=subprocess.STDOUT)
    except:
        print("cannot run telegraf once")
     
    
        
def main(argv): 
    load_program_config()    
 
    signal.signal(signal.SIGINT, sig_handler)
    
    # Run Telegraf once to get up-to-date data
    run_telegraf_once_thread =  Thread(target=run_telegraf_once)
    run_telegraf_once_thread.start()

    #aiohttp
    FernetKey = '6ip63k7p0jh5rR/2Bs4AdSM35FMQWovGwSz0tydU6ro='
    #middleware = session_middleware(SimpleCookieStorage())
    middleware = session_middleware(EncryptedCookieStorage(FernetKey))

    app = web.Application(middlewares=[middleware])
    app.router.add_route('GET', '/states', serve_states)
    app.router.add_route('GET', '/state_series', serve_state_series)
    app.router.add_route('POST', '/telegraf', process_telegraf_post)

    

    # https://github.com/bugov/aiohttp-basicauth-middleware
    """
    app.middlewares.append(
    basic_auth_middleware(
        ('/states',),
        {'user': 'password'},
    )
    )
    """
    

    app.middlewares.append(
    basic_auth_middleware(
        ('/channel/','/editor/'),
        {'arska': 'bceeffe128eb5f0f76a7c9f7c3d93fededa859f0f1689e00ff7bff4b93c7ed97206d2844a2e3327fc14edc9e36ce4601a5409bb1a34bda332715acb24b5cbc5e'},
        lambda x: hashlib.sha512(bytes(x, encoding='utf-8')).hexdigest(),
    )
    )
    #generate digest manually: echo -n 'my_new_password'|openssl dgst -sha512


    web.run_app(app, host=arska.get_setting("host_ip"), port=arska.get_setting("host_port"))
   #TODO: this could be main loop where recalculation are started after new data arrived from Telegraf
    while True:
        pass
    


if __name__ == "__main__":
    main(sys.argv[1:])
    

