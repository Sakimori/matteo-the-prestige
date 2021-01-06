import time, asyncio, jsonpickle, random, math
from games import team, game
from discord import Embed, Color
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
    def __init__(self, name, team_dic, series_length = 5, finals_series_length = 7, max_innings = 9, id = None, secs_between_games = 300, secs_between_rounds = 600): 
        self.name = name
        self.teams = team_dic #same format as division, wins/losses will be used for seeding later
        self.bracket = None
        self.results = None
        self.series_length = series_length
        self.finals_length = finals_series_length
        self.game_length = max_innings
        self.active = False
        self.delay = secs_between_games
        self.round_delay = secs_between_rounds
        self.finals = False
        self.id = id

        if id is None:
            self.id = random.randint(1111,9999)
        else:
            self.id = id


    def build_bracket(self, random_sort = False, by_wins = False):
        teams_list = list(self.teams.keys()).copy()

        if random_sort:
            def sorter(team_in_list):
                return random.random()

        elif by_wins:
            def sorter(team_in_list):
                return self.teams[team_in_list]["wins"] #sorts by wins

        else: #sort by average stars
            def sorter(team_in_list):
                return team_in_list.average_stars()

        teams_list.sort(key=sorter, reverse=True)
        

        bracket_layers = int(math.ceil(math.log(len(teams_list), 2)))
        empty_slots = int(math.pow(2, bracket_layers) - len(teams_list))

        for i in range(0, empty_slots):
            teams_list.append(None)

        previous_bracket_layer = teams_list.copy()
        for i in range(0, bracket_layers - 1):
            this_layer = []
            for pair in range(0, int(len(previous_bracket_layer)/2)):
                if pair % 2 == 0: #if even number
                    this_layer.insert(0+int(pair/2), [previous_bracket_layer.pop(0), previous_bracket_layer.pop(-1)]) #every other pair goes at front of list, moving forward
                else:
                    this_layer.insert(0-int((1+pair)/2), [previous_bracket_layer.pop(int(len(previous_bracket_layer)/2)-1), previous_bracket_layer.pop(int(len(previous_bracket_layer)/2))]) #every other pair goes at end of list, moving backward
            previous_bracket_layer = this_layer
        self.bracket = bracket(previous_bracket_layer, bracket_layers)

    def round_check(self):
        if self.bracket.depth == 1:
            self.finals = True
            return True
        else:
            return False

class bracket(object):
    this_bracket = []

    def __init__(self, bracket_list, depth):
        self.this_bracket = bracket_list
        self.depth = depth
        self.bottom_row = []

    def get_bottom_row(self):
        self.depth = 1
        self.bottom_row = []
        self.dive(self.this_bracket)
        return self.bottom_row

    def dive(self, branch):
        if not isinstance(branch[0], list): #if it's a pair of games
            self.bottom_row.append(branch)
        else:
            self.depth += 1
            return self.dive(branch[0]), self.dive(branch[1])

    def set_winners_dive(self, winners_list, index = 0, branch = None, parent = None):
        if branch is None:
            branch = self.this_bracket.copy()
        if not isinstance(branch[0], list): #if it's a pair of games
            if branch[0].name in winners_list or branch[1] is None:
                winner = branch[0]
                if parent is not None:
                    parent[index] = winner
            elif branch[1].name in winners_list:
                winner = branch[1]
                if parent is not None:
                    parent[index] = winner        
        else:
            self.set_winners_dive(winners_list, index = 0, branch = branch[0], parent = branch)
            self.set_winners_dive(winners_list, index = 1, branch = branch[1], parent = branch)

        if parent is None:
            self.this_bracket = branch
            return branch