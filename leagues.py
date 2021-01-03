import time, asyncio, jsonpickle, random, math
from games import team, game
import database as db





class league(object):
    def __init__(self, name, subleagues_dic):
        self.subleagues = {} #key: name, value: [divisions]
        self.max_days
        self.day = 1
        self.name = name
        self.subleagues = subleagues_dic

class division(object):
    def __init__(self):
        self.teams = {} #key: team object, value: {wins; losses; run diff}

class tournament(object):
    def __init__(self, team_dic): 
        self.teams = {} #same format as division, wins/losses will be used for seeding later
        self.bracket = {}
        self.bracket_layers = 0

    def build_bracket(self, random = False, by_wins = False):
        teams_list = self.teams.keys().copy()

        if random:
            def sorter(team_in_list):
                return random.random()

        elif by_wins:
            def sorter(team_in_list):
                return self.teams[team_in_list][0] #sorts by wins

        if not random and not by_wins: #sort by average stars
            def sorter(team_in_list):
                return team_in_list.average_stars()

        teams_list.sort(key=sorter, reverse=True)

        self.bracket_layers = int(math.ceil(math.log(len(teams_list), 2)))
        empty_slots = int(math.pow(2, bracket_layers) - len(teams_list))

        for i in range(0, empty_slots):
            teams_list.append(None)
