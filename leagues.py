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
        self.historic = False
        self.owner = None
        self.season = 1
        self.autoplay = -1
        self.champions = {}

    def setup(self, league_dic, division_games = 1, inter_division_games = 1, inter_league_games = 1, games_per_hour = 2):
        self.league = league_dic # { subleague name : { division name : [team object] } }
        self.constraints = {
            "division_games" : division_games,
            "inter_div_games" : inter_division_games,
            "inter_league_games" : inter_league_games,
            "division_leaders" : 0,
            "wild_cards" : 0
            }
        self.day = 1
        self.schedule = {}
        self.series_length = 3 #can be changed
        self.game_length = None
        self.active = False
        self.games_per_hour = games_per_hour

    def add_stats_from_game(self, players_dic):
        league_db.add_stats(self.name, players_dic)

    def update_standings(self, results_dic):
        league_db.update_standings(self.name, results_dic)


    def last_series_check(self):
        return str(math.ceil((self.day)/self.series_length) + 1) not in self.schedule.keys()

    def day_to_series_num(self, day):
        return math.ceil((self.day)/self.series_length)

    def tiebreaker_required(self):
        standings = {}
        matchups = []
        tournaments = []
        for team_name, wins, losses, run_diff in league_db.get_standings(self.name):
            standings[team_name] = {"wins" : wins, "losses" : losses, "run_diff" : run_diff}

        for subleague in iter(self.league.keys()):
            team_dic = {}          
            subleague_array = []
            wildcard_leaders = []
            for division in iter(self.league[subleague].keys()):
                division_standings = []
                division_standings += self.division_standings(self.league[subleague][division], standings)
                division_leaders = division_standings[:self.constraints["division_leaders"]]
                for division_team, wins, losses, diff, gb in division_standings[self.constraints["division_leaders"]:]:
                    if division_team.name != division_leaders[-1][0].name and standings[division_team.name]["wins"] == standings[division_leaders[-1][0].name]["wins"]:
                        matchups.append((division_team, division_standings[self.constraints["division_leaders"]-1][0], f"{division} Tiebreaker"))

                this_div_wildcard = [this_team for this_team, wins, losses, diff, gb in self.division_standings(self.league[subleague][division], standings)[self.constraints["division_leaders"]:]]
                subleague_array += this_div_wildcard
            if self.constraints["wild_cards"] > 0:
                wildcard_standings = self.division_standings(subleague_array, standings)
                wildcard_leaders = wildcard_standings[:self.constraints["wild_cards"]]
                for wildcard_team, wins, losses, diff, gb in wildcard_standings[self.constraints["wild_cards"]:]:
                    if wildcard_team.name != wildcard_leaders[-1][0].name and standings[wildcard_team.name]["wins"] == standings[wildcard_leaders[-1][0].name]["wins"]:
                        matchups.append((wildcard_team, wildcard_standings[self.constraints["wild_cards"]-1][0], f"{subleague} Wildcard Tiebreaker"))
        
        for team_a, team_b, type in matchups:
            tourney = tournament(f"{self.name} {type}",{team_a : {"wins" : 1}, team_b : {"wins" : 0}}, finals_series_length=1, secs_between_games=int(3600/self.games_per_hour), secs_between_rounds=int(7200/self.games_per_hour))
            tourney.build_bracket(by_wins = True)
            tourney.league = self
            tournaments.append(tourney)
        return tournaments

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
                if str(day) in self.schedule.keys():
                    for game_on_day in self.schedule[str(day)]:
                        for team in game:
                            if team in game_on_day:
                                found = True
                    if not found:
                        self.schedule[str(day)].append(game)
                        scheduled = True
                else:
                    self.schedule[str(day)] = [game]
                    scheduled = True
                day += 1

    def division_standings(self, division, standings):
        def sorter(team_in_list):
            if team_in_list[2] == 0 and team_in_list[1] == 0:
                return (0, team_in_list[3])
            return (team_in_list[1]/(team_in_list[1]+team_in_list[2]), team_in_list[3])

        teams = division.copy()
        
        for index in range(0, len(teams)):
            this_team = teams[index]
            teams[index] = [this_team, standings[teams[index].name]["wins"], standings[teams[index].name]["losses"], standings[teams[index].name]["run_diff"], 0]

        teams.sort(key=sorter, reverse=True)
        return teams

    def season_length(self):
        return self.constraints["division_games"]*(len(random.choice(random.choice(self.league))-1)) + self.constraints["inter_div_games"] + self.constraints["inter_league_games"]

    def standings_embed(self):
        this_embed = Embed(color=Color.purple(), title=self.name)
        standings = {}
        for team_name, wins, losses, run_diff in league_db.get_standings(self.name):
            standings[team_name] = {"wins" : wins, "losses" : losses, "run_diff" : run_diff}
        for subleague in iter(self.league.keys()):
            this_embed.add_field(name="Subleague:", value=f"**{subleague}**", inline = False)
            for division in iter(self.league[subleague].keys()):
                teams = self.division_standings(self.league[subleague][division], standings)

                for index in range(0, len(teams)):
                    if index == self.constraints["division_leaders"] - 1:
                        teams[index][4] = "-"
                    else:
                        games_behind = ((teams[self.constraints["division_leaders"] - 1][1] - teams[index][1]) + (teams[index][2] - teams[self.constraints["division_leaders"] - 1][2]))/2
                        teams[index][4] = games_behind
                teams_string = ""
                for this_team in teams:
                    if this_team[2] != 0 or this_team[1] != 0:
                        teams_string += f"**{this_team[0].name}\n**{this_team[1]} - {this_team[2]} WR: {round(this_team[1]/(this_team[1]+this_team[2]), 3)} GB: {this_team[4]}\n\n"
                    else:
                        teams_string += f"**{this_team[0].name}\n**{this_team[1]} - {this_team[2]} WR: - GB: {this_team[4]}\n\n"

                this_embed.add_field(name=f"{division} Division:", value=teams_string, inline = False)
        
        this_embed.set_footer(text=f"Standings as of day {self.day-1} / {self.season_length()}")
        return this_embed

    def wildcard_embed(self):
        this_embed = Embed(color=Color.purple(), title=f"{self.name} Wildcard Race")
        standings = {}
        for team_name, wins, losses, run_diff in league_db.get_standings(self.name):
            standings[team_name] = {"wins" : wins, "losses" : losses, "run_diff" : run_diff}
        for subleague in iter(self.league.keys()):
            subleague_array = []
            for division in iter(self.league[subleague].keys()):
                this_div = [this_team for this_team, wins, losses, diff, gb in self.division_standings(self.league[subleague][division], standings)[self.constraints["division_leaders"]:]]
                subleague_array += this_div

            teams = self.division_standings(subleague_array, standings)
            teams_string = ""
            for index in range(0, len(teams)):
                if index == self.constraints["wild_cards"] - 1:
                    teams[index][4] = "-"
                else:
                    games_behind = ((teams[self.constraints["wild_cards"] - 1][1] - teams[index][1]) + (teams[index][2] - teams[self.constraints["wild_cards"] - 1][2]))/2
                    teams[index][4] = games_behind

            for this_team in teams:
                if this_team[2] != 0 or this_team[1] != 0:
                    teams_string += f"**{this_team[0].name}\n**{this_team[1]} - {this_team[2]} WR: {round(this_team[1]/(this_team[1]+this_team[2]), 3)} GB: {this_team[4]}\n\n"
                else:
                    teams_string += f"**{this_team[0].name}\n**{this_team[1]} - {this_team[2]} WR: - GB: {this_team[4]}\n\n"

            this_embed.add_field(name=f"{subleague} League:", value=teams_string, inline = False)
        
        this_embed.set_footer(text=f"Wildcard standings as of day {self.day-1}")
        return this_embed

    def champ_series(self):
        tournaments = []
        standings = {}
        
        for team_name, wins, losses, run_diff in league_db.get_standings(self.name):
            standings[team_name] = {"wins" : wins, "losses" : losses, "run_diff" : run_diff}

        for subleague in iter(self.league.keys()):
            team_dic = {}
            division_leaders = []
            subleague_array = []
            wildcard_leaders = []
            for division in iter(self.league[subleague].keys()):
                division_leaders += self.division_standings(self.league[subleague][division], standings)[:self.constraints["division_leaders"]]                
                this_div_wildcard = [this_team for this_team, wins, losses, diff, gb in self.division_standings(self.league[subleague][division], standings)[self.constraints["division_leaders"]:]]
                subleague_array += this_div_wildcard
            if self.constraints["wild_cards"] > 0:
                wildcard_leaders = self.division_standings(subleague_array, standings)[:self.constraints["wild_cards"]]

            for this_team, wins, losses, diff, gb in division_leaders + wildcard_leaders:
                team_dic[this_team] = {"wins" : wins}
            
            subleague_tournament = tournament(f"{self.name} {subleague} Championship Series", team_dic, series_length=3, finals_series_length=5, secs_between_games=int(3600/self.games_per_hour), secs_between_rounds=int(7200/self.games_per_hour))
            subleague_tournament.build_bracket(by_wins = True)
            subleague_tournament.league = self
            tournaments.append(subleague_tournament)

        tournaments[0].increment = True
        return tournaments


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
        self.league = None
        self.winner = None
        self.increment = False

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
        with open(os.path.join(data_dir, league_dir, this_league.name, f"{this_league.name}.league"), "w") as league_file:
            league_json_string = jsonpickle.encode(this_league.league, keys=True)
            json.dump(league_json_string, league_file, indent=4)
    league_db.save_league(this_league)

def load_league_file(league_name):
    if league_db.league_exists(league_name):
        state = league_db.state(league_name)
        this_league = league_structure(league_name)
        with open(os.path.join(data_dir, league_dir, league_name, f"{this_league.name}.league")) as league_file:
            this_league.league = jsonpickle.decode(json.load(league_file), keys=True, classes=team)
        with open(os.path.join(data_dir, league_dir, league_name, f"{this_league.name}.state")) as state_file:
            state_dic = json.load(state_file)

        this_league.day = state_dic["day"]
        this_league.schedule = state_dic["schedule"]
        this_league.constraints = state_dic["constraints"]
        this_league.game_length = state_dic["game_length"]
        this_league.series_length = state_dic["series_length"]
        this_league.owner = state_dic["owner"]
        this_league.games_per_hour = state_dic["games_per_hour"]
        this_league.historic = state_dic["historic"]
        this_league.season = state_dic["season"]
        try:
            this_league.champions = state_dic["champions"]
        except:
            this_league.champions = {}
        return this_league