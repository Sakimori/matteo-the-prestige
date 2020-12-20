#interfaces with onomancer

import requests
import json
import database as db


onomancer_url = "https://onomancer.sibr.dev/api/"
name_stats_hook = "generateStats/"

def get_stats(username):
    #check database for cached name first

    #yell at onomancer
    response = requests.get(onomancer_url + name_stats_hook + username)
    if response.status_code == 200:
        return response.json()