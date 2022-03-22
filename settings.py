import os
import json


# if runs under other user id (e.g. Telegraf) takes parent folder from python script (must start with . )
def replace_path_from_script(file_name):
    if file_name[0]==".":
        return os.path.dirname(__file__) + file_name[1:]
    else:
        return file_name


def read_settings(settings_filename=""):
    settings_filename = replace_path_from_script(settings_filename)
    if os.path.exists(settings_filename):
        with open(settings_filename, "r") as file:
            settings_string = ""
            for line in file:
                if line.strip().startswith('#'):
                    continue  # skip comments
                settings_string += line 
            ls = json.loads(settings_string)
    else:      
        ls = json.loads("{}") 
    return ls


arska_file_name = "./settings/arska.json"
states_filename =  "./settings/states.json"
#cache files
dayahead_file_name = "./data/dayahead.json"
forecastpv_file_name = "./data/forecastpv.json"










