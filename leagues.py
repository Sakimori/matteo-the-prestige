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
        self.teams = {} #key: team object, value: {wins; rd (run diff)}

class tournament(object):
    def __init__(self, name, team_dic, series_length = 5, max_innings = 9): 
        self.name = name
        self.teams = team_dic #same format as division, wins/losses will be used for seeding later
        self.bracket = None
        self.results = None
        self.series_length = series_length
        self.game_length = max_innings
        self.active = False

    def build_bracket(self, random_sort = False, by_wins = False):
        teams_list = list(self.teams.keys()).copy()

        if random_sort:
            def sorter(team_in_list):
                return random.random()

        elif by_wins:
            def sorter(team_in_list):
                return self.teams[team_in_list][0] #sorts by wins

        else: #sort by average stars
            def sorter(team_in_list):
                return team_in_list.average_stars()

        teams_list.sort(key=sorter, reverse=True)

        bracket_layers = int(math.ceil(math.log(len(teams_list), 2)))
        empty_slots = int(math.pow(2, bracket_layers) - len(teams_list))

        for i in range(0, empty_slots):
            teams_list.append(None)

        previous_bracket_layer = teams_list.copy()
        for i in range(0, bracket_layers-1):
            this_layer = []
            for pair in range(0, int(len(previous_bracket_layer)/2)):
                if pair % 2 == 0: #if even number
                    this_layer.insert(0+int(pair/2), [previous_bracket_layer.pop(0), previous_bracket_layer.pop(-1)]) #every other pair goes at front of list, moving forward
                else:
                    this_layer.insert(0-int((1+pair)/2), [previous_bracket_layer.pop(0), previous_bracket_layer.pop(-1)]) #every other pair goes at end of list, moving backward
            previous_bracket_layer = this_layer
        self.bracket = bracket(previous_bracket_layer, bracket_layers)
        self.bracket.get_bottom_row()

class bracket(object):
    def __init__(self, bracket_list, depth):
        self.this_bracket = bracket_list
        self.depth = depth
        self.bottom_row = []

    def get_bottom_row(self):
        self.bottom_row = []
        self.dive(self.this_bracket)
        return self.bottom_row

    def dive(self, branch):
        if not isinstance(branch[0], list): #if it's a pair of games
            self.bottom_row.append(branch)
        else:
            return self.dive(branch[0]), self.dive(branch[1])