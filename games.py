import json, random, os, math
from enum import Enum
import database as db

def config():
    if not os.path.exists("games_config.json"):
        #generate default config
        config_dic = {
                "default_length" : 3,
                "stlat_weights" : {
                        "batting_stars" : 1, #batting
                        "pitching_stars" : 1, #pitching
                        "baserunning_stars" : 1, #baserunning
                        "defense_stars" : 1 #defense
                    }
            }
        with open("games_config.json", "w") as config_file:
            json.dump(config_dic, config_file, indent=4)
            return config_dic
    else:
        with open("games_config.json") as config_file:
            return json.load(config_file)

class appearance_outcomes(Enum):
    strikeoutlooking = "strikes out looking."
    strikeoutswinging = "strikes out swinging."
    groundout = "grounds out to"
    flyout = "flies out to"
    fielderschoice = "reaches on fielder's choice."
    doubleplay = "grounds into a double play!"
    walk = "draws a walk."
    single = "hits a single!"
    double = "hits a double!"
    triple = "hits a triple!"
    homerun = "hits a home run!"
    grandslam = "hits a grand slam!"


class player(object):
    def __init__(self, json_string):
        self.stlats = json.loads(json_string)
        self.id = self.stlats["id"]
        self.name = self.stlats["name"]
        self.game_stats = {}


class team(object):
    def __init__(self):
        self.name = None
        self.lineup = []
        self.lineup_position = 0
        self.pitcher = None

    def add_lineup(self, new_player):
        if len(self.lineup) <= 12:
            self.lineup.append(new_player)
            return (True,)
        else:
            return (False, "12 players in the lineup, maximum. We're being generous here.")
    
    def set_pitcher(self, new_player):
        self.pitcher = new_player
        return (True,)

    def is_ready(self):
        return (len(self.lineup) >= 1 and self.pitcher is not None)

    def finalize(self):
        if self.is_ready():
            while len(self.lineup) <= 4:
                self.lineup.append(random.choice(self.lineup))
            return True
        else: 
            return False


class game(object):

    def __init__(self, team1, team2, length=None):
        self.teams = {"away" : team1, "home" : team2}
        self.inning = 1
        self.top_of_inning = True
        if length is not None:
            self.max_innings = length
        else:
            self.max_innings = config()["default_length"]
        self.bases = {1 : None, 2 : None, 3 : None}

    def get_batter(self):
        if self.top_of_inning:
            bat_team = self.teams["away"]
        else:
            bat_team = self.teams["home"]
        return bat_team.lineup[bat_team.lineup_position % len(bat_team.lineup)]

    def get_pitcher(self):
        if self.top_of_inning:
            return self.teams["home"].pitcher
        else:
            return self.teams["away"].pitcher

    def at_bat(self):
        pitcher = self.get_pitcher()
        batter = self.get_batter()
        if self.top_of_inning:
            defender = random.choice(self.teams["home"].lineup)
        else:
            defender = random.choice(self.teams["away"].lineup)

        bat_stat = random_star_gen("batting_stars", batter)
        pitch_stat = random_star_gen("pitching_stars", pitcher)
        def_stat = random_star_gen("defense_stars", defender)
        pb_system_stat = (random.gauss(1*math.erf((bat_stat - pitch_stat)*1.5)-1.8,2.2))
        hitnum = random.gauss(2*math.erf(bat_stat/4)-1,3)


        outcome = {}
        if pb_system_stat <= 0:
            outcome["ishit"] = False
            fc_flag = False
            if hitnum < -1.5:
                outcome["text"] = random.choice([appearance_outcomes.strikeoutlooking, appearance_outcomes.strikeoutswinging])
            elif hitnum < 1:
                outcome["text"] = appearance_outcomes.groundout
                outcome["defender"] = defender
            elif hitnum < 4: 
                outcome["text"] = appearance_outcomes.flyout
                outcome["defender"] = defender
            else:
                outcome["text"] = appearance_outcomes.walk

            if self.bases[1] is not None and hitnum < 1:
                outcome["text"] = appearance_outcomes.doubleplay
            for base in self.bases.values():
                if base is not None:
                    fc_flag = True
            if fc_flag and 1 <= hitnum and hitnum < 2:
                outcome["text"] = appearance_outcomes.fielderschoice
        else:
            outcome["ishit"] = True
            if hitnum < 1:
                outcome["text"] = appearance_outcomes.single
            elif hitnum < 2.85:
                outcome["text"] = appearance_outcomes.double
            elif hitnum < 3.1:
                outcome["text"] = appearance_outcomes.triple
            else:
                if self.bases[1] is not None and self.bases[2] is not None and self.bases[3] is not None:
                    outcome["text"] = appearance_outcomes.grandslam
                else:
                    outcome["text"] = appearance_outcomes.homerun

        if self.top_of_inning:
            self.teams["away"].lineup_position += 1
        else:
           self.teams["home"].lineup_position += 1
        return outcome
        


def random_star_gen(key, player):
    return random.gauss(config()["stlat_weights"][key] * player.stlats[key],1)
#    innings_pitched
#    walks_allowed
#    strikeouts_given
#    runs_allowed
#    plate_appearances
#    walks
#    hits
#    total_bases
#    rbis
#    walks_taken
#    strikeouts_taken


