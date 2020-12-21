#interfaces with onomancer

import requests, json, urllib
import database as db


onomancer_url = "https://onomancer.sibr.dev/api/"
name_stats_hook = "generateStats2?name="

def get_stats(name):
    #yell at onomancer if not in cache or too old
    response = requests.get(onomancer_url + name_stats_hook + urllib.parse.quote_plus(name))
    if response.status_code == 200:  
        return response.json()

def get_scream(username):
    scream = db.get_soulscream(username)
    if scream is not None:
        return scream
    else:
        scream = get_stats(username)["soulscream"]
        db.cache_soulscream(username, scream)
        return scream