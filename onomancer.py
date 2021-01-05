#interfaces with onomancer

import requests, json, urllib
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import database as db


onomancer_url = "https://onomancer.sibr.dev/api/"
name_stats_hook = "getOrGenerateStats?name="
collection_hook = "getCollection?token="
names_hook = "getNames"


def _retry_session(retries=3, backoff=0.3, status=(500, 501, 502, 503, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff,
        status_forcelist=status,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session

def get_stats(name):
    player = db.get_stats(name)
    if player is not None:
        return player #returns json_string

    #yell at onomancer if not in cache or too old
    response = _retry_session().get(onomancer_url + name_stats_hook + urllib.parse.quote_plus(name))
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
    response = _retry_session().get(onomancer_url + collection_hook + urllib.parse.quote(collection_url))
    if response.status_code == 200:
        for player in response.json()['lineup'] + response.json()['rotation']:
            db.cache_stats(player['name'], json.dumps(player))

        return json.dumps(response.json())


def get_names(limit=20, threshold=1):
    """
    Get `limit` random players that have at least `threshold` upvotes.
    Returns dictionary keyed by player name of stats.
    """
    response = _retry_session().get(
        onomancer_url + names_hook,
        params={
            'limit': limit,
            'threshold': threshold,
            'with_stats': 1,
            'random': 1,
        },
    )
    response.raise_for_status()
    res = {}
    for stats in response.json():
        name = stats['name']
        db.cache_stats(name, json.dumps(stats))
        res[name] = stats
    return res
