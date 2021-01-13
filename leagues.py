import time, asyncio, json, jsonpickle, random, math, os
import league_storage as league_db
from itertools import chain
from games import team, game
from discord import Embed, Color

data_dir = "data"
league_dir = "leagues"

class league_structure(object):
    def __init__(self, name):
        self.name = name

    def setup(self, league_dic, division_games = 1, inter_division_games = 1, inter_league_games = 1, games_per_hour = 2):
        self.league = league_dic #key: subleague, value: {division : team_name}
        self.constraints = {
            "division_games" : division_games,
            "inter_div_games" : inter_division_games,
            "inter_league_games" : inter_league_games
            }
        self.day = 1
        self.schedule = {}
        self.series_length = 3 #can be changed
        self.game_length = None
        self.active = False
        self.games_per_hour = games_per_hour

    def add_stats_from_game(self, players_list):
        league_db.add_stats(players_list)

    def update_standings(self, results_dic):
        league_db.update_standings(self.name, results_dic)


    def last_series_check(self):
        return self.day + 1 in self.schedule.keys()

    def find_team(self, team_name):
        for subleague in iter(self.league.keys()):
            for division in iter(self.league[subleague].keys()):
                if team_name in self.league[subleague][division]:
                    return (subleague, division)

    def teams_in_league(self):
        teams = []
        for division in self.league.values():
            for teams_list in division.values():
                teams += teams_list
        return teams

    def teams_in_subleague(self, subleague_name):
        teams = []
        if subleague_name in self.league.keys():
            for division_list in self.league[subleague_name].values():
                teams += division_list
            return teams
        else:
            print("League not found.")
            return None

    def teams_in_division(self, subleague_name, division_name):
        if subleague_name in self.league.keys() and division_name in self.league[subleague_name].keys():
            return self.league[subleague_name][division_name]
        else:
            print("Division in that league not found.")
            return None

    def make_matchups(self):
        matchups = []
        batch_subleagues = [] #each sub-array is all teams in each subleague
        subleague_max = 1
        for subleague in self.league.keys():
            teams = self.teams_in_subleague(subleague)
            if subleague_max < len(teams):
                subleague_max = len(teams)
            batch_subleagues.append(teams)

        for subleague in batch_subleagues:
            while len(subleague) < subleague_max:
                subleague.append("OFF")
   
        for i in range(0, self.constraints["inter_league_games"]): #generates inter-league matchups
            unmatched_indices = [i for i in range(0, len(batch_subleagues))]
            for subleague_index in range(0, len(batch_subleagues)):
                if subleague_index in unmatched_indices:
                    unmatched_indices.pop(unmatched_indices.index(subleague_index))
                    match_with_index = random.choice(unmatched_indices)
                    unmatched_indices.pop(unmatched_indices.index(match_with_index))
                    league_a = batch_subleagues[subleague_index].copy()
                    league_b = batch_subleagues[match_with_index].copy()
                    random.shuffle(league_a)
                    random.shuffle(league_b)
                    a_home = True
                    for team_a, team_b in zip(league_a, league_b):
                        if a_home:
                            matchups.append([team_b.name, team_a.name])
                        else:
                            matchups.append([team_a.name, team_b.name])
                        a_home != a_home
                    
        for i in range(0, self.constraints["inter_div_games"]): #inter-division matchups
            for subleague in self.league.keys():
                division_max = 1
                divisions = []
                for div in self.league[subleague].keys():
                    if division_max < len(self.league[subleague][div]):
                        divison_max = len(self.league[subleague][div])
                    divisions.append(self.league[subleague][div])

                last_div = None
                if len(divisions) % 2 != 0:
                    if division_max % 2 != 0:
                        divisions.append(["OFF" for i in range(0, division_max)])
                    else:
                        last_div = divisions.pop
    
                divs_a = list(chain(divisions[int(len(divisions)/2):]))[0]
                if last_div is not None:
                    divs_a.extend(last_div[int(len(last_div)/2):])
                random.shuffle(divs_a)
            
                divs_b = list(chain(divisions[:int(len(divisions)/2)]))[0]
                if last_div is not None:
                    divs_a.extend(last_div[:int(len(last_div)/2)])
                random.shuffle(divs_b)

                a_home = True
                for team_a, team_b in zip(divs_a, divs_b):
                    if a_home:
                        matchups.append([team_b.name, team_a.name])
                    else:
                        matchups.append([team_a.name, team_b.name])
                    a_home != a_home


        for subleague in self.league.keys():
            for division in self.league[subleague].values(): #generate round-robin matchups
                if len(division) % 2 != 0:
                    division.append("OFF")

                for i in range(0, len(division)-1):
                    teams_a = division[int(len(division)/2):]
                    teams_b = division[:int(len(division)/2)]
                    teams_b.reverse()

                    for team_a, team_b in zip(teams_a, teams_b):
                        for j in range(0, self.constraints["division_games"]):
                            if i % 2 == 0:
                                matchups.append([team_b.name, team_a.name])
                            else:
                                matchups.append([team_a.name, team_b.name])

                        division.insert(1, division.pop())
        return matchups       
    
    def generate_schedule(self):
        matchups = self.make_matchups()
        random.shuffle(matchups)
        for game in matchups:
            scheduled = False      
            day = 1
            while not scheduled:
                found = False
                if day in self.schedule.keys():
                    for game_on_day in self.schedule[day]:
                        for team in game:
                            if team in game_on_day:
                                found = True
                    if not found:
                        self.schedule[day].append(game)
                        scheduled = True
                else:
                    self.schedule[day] = [game]
                    scheduled = True
                day += 1

class tournament(object):
    def __init__(self, name, team_dic, series_length = 5, finals_series_length = 7, max_innings = 9, id = None, secs_between_games = 300, secs_between_rounds = 600): 
        self.name = name
        self.teams = team_dic #key: team object, value: wins
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


    def build_bracket(self, random_sort = False, by_wins = False, manual = False):
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
    
        if not manual:
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

def save_league(this_league):
    if not league_db.league_exists(this_league.name):
        league_db.init_league_db(this_league)
        with open(os.path.join(data_dir, league_dir, f"{this_league.name}.league"), "w") as league_file:
            league_json_string = jsonpickle.encode(this_league.league, keys=True)
            json.dump(league_json_string, league_file, indent=4)
        return True

def load_league_file(league_name):
    if league_db.league_exists(league_name):
        state = league_db.state(league_name)
        this_league = league_structure(league_name)
        with open(os.path.join(data_dir, league_dir, f"{this_league.name}.league")) as league_file:
            this_league.league = jsonpickle.decode(json.load(league_file), keys=True, classes=team)
        with open(os.path.join(data_dir, league_dir, f"{this_league.name}.state")) as state_file:
            state_dic = json.load(state_file)
        return this_league