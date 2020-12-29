#interfaces with onomancer

import requests, json, urllib
import database as db


onomancer_url = "https://onomancer.sibr.dev/api/"
name_stats_hook = "generateStats2?name="
collection_hook = "getCollection?token="

def get_stats(name):
    player = db.get_stats(name)
    if player is not None:
        return player #returns json_string

    #yell at onomancer if not in cache or too old
    response = requests.get(onomancer_url + name_stats_hook + urllib.parse.quote_plus(name))
    if response.status_code == 200:
        stats = json.dumps(response.json())
        db.cache_stats(name, stats)
        return stats

def get_scream(username):
    scream = db.get_soulscream(username)
    if scream is not None:
        return scream
    else:
        scream = json.loads(get_stats(username))["soulscream"]
        db.cache_soulscream(username, scream)
        return scream

def get_collection(collection_url):
    response = requests.get(onomancer_url + collection_hook + urllib.parse.quote(collection_url))
    if response.status_code == 200:
        for player in response.json()['lineup'] + response.json()['rotation']:
            db.cache_stats(player['name'], json.dumps(player))

        return json.dumps(response.json())