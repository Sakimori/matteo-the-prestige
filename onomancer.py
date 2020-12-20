#interfaces with onomancer

import requests
import json

onomancer_url = "https://onomancer.sibr.dev/api/"
name_stats_hook = "generateStats/"

def get_stats(username):
    response = requests.get(onomancer_url + name_stats_hook + username)
    if response.status_code == 200:
        return response.json