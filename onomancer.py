#interfaces with onomancer

import requests
import json
import database as db


onomancer_url = "https://onomancer.sibr.dev/api/"
name_stats_hook = "generateStats/"

def get_stats(username):
    #check database for cached name first
    scream = db.get_soulscream(username)
    if scream is not None:
        return scream

    #yell at onomancer if not in cache or too old
    response = requests.get(onomancer_url + name_stats_hook + username)
    print("yelled at onomancer")
    if response.status_code == 200:
        db.cache_soulscream(username, response.json()["soulscream"])
        return response.json()["soulscream"]