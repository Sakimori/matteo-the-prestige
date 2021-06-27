from lxml import html
import requests, json
import onomancer as ono


def random_real_player():
    name = []
    while name == []:
        page = requests.get("http://www.baseball-reference.com/rand.fcgi")
        tree = html.fromstring(page.content)
        name = tree.xpath("//h1[@itemprop='name']/span/text()")
        if len(name) > 0 and len(name[0]) == 4:
            name = [] #gets rid of years
    name = name[0]
    return name

def get_real_players(num):
    names = []
    for i in range(0, num):
        names.append(random_real_player())
    players = {}
    for name in names:
        players[name] = json.loads(ono.get_stats(name))
    return players