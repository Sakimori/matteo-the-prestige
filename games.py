import json, random, os, math, jsonpickle
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
    sacrifice = "hits a sacrifice fly towards"
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
        self.game_stats = {
                            "outs_pitched" : 0,
                            "walks_allowed" : 0,
                            "hits_allowed" : 0,
                            "strikeouts_given" : 0,
                            "runs_allowed" : 0,
                            "plate_appearances" : 0,
                            "walks_taken" : 0,
                            "sacrifices" : 0,
                            "hits" : 0,
                            "home_runs" : 0,
                            "total_bases" : 0,
                            "rbis" : 0,
                            "strikeouts_taken" : 0
            }

    def star_string(self, key):
        str_out = ""
        starstring = str(self.stlats[key])
        if ".5" in starstring:
            starnum = int(starstring[0])
            addhalf = True
        else:
            starnum = int(starstring[0])
            addhalf = False
        str_out += "⭐" * starnum
        if addhalf:
            str_out += "✨"
        return str_out

    def __str__(self):
        return self.name


class team(object):
    def __init__(self):
        self.name = None
        self.lineup = []
        self.lineup_position = 0
        self.pitcher = None
        self.score = 0
        self.slogan = None

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

    def prepare_for_save(self):
        self.lineup_position = 0
        self.score = 0
        for this_player in self.lineup:
            for stat in this_player.game_stats.keys():
                this_player.game_stats[stat] = 0
        return True

    def finalize(self):
        if self.is_ready():
            while len(self.lineup) <= 4:
                self.lineup.append(random.choice(self.lineup))
            return True
        else: 
            return False


class game(object):

    def __init__(self, name, team1, team2, length=None):
        self.name = name
        self.over = False
        self.teams = {"away" : team1, "home" : team2}
        self.inning = 1
        self.outs = 0
        self.top_of_inning = True
        self.last_update = None
        self.owner = None
        self.ready = False
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
        outcome = {}
        pitcher = self.get_pitcher()
        batter = self.get_batter()

        if self.top_of_inning:
            defender = random.choice(self.teams["home"].lineup)
        else:
            defender = random.choice(self.teams["away"].lineup)

        outcome["batter"] = batter
        outcome["defender"] = ""

        bat_stat = random_star_gen("batting_stars", batter)
        pitch_stat = random_star_gen("pitching_stars", pitcher)
        pb_system_stat = (random.gauss(1*math.erf((bat_stat - pitch_stat)*1.5)-1.8,2.2))
        hitnum = random.gauss(2*math.erf(bat_stat/4)-1,3)


        
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

            if self.bases[1] is not None and hitnum < -1.3 and self.outs != 2:
                outcome["text"] = appearance_outcomes.doubleplay
                outcome["defender"] = ""

            for base in self.bases.values():
                if base is not None:
                    fc_flag = True

            if fc_flag and self.outs < 2:
                if 0 <= hitnum and hitnum < 1.5:
                    outcome["text"] = appearance_outcomes.fielderschoice
                    outcome["defender"] = ""
                elif 2.5 <= hitnum:
                    if self.bases[2] is not None or self.bases[3] is not None:
                        outcome["advance"] = True
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
        return outcome

    def baserunner_check(self, defender, outcome):
        def_stat = random_star_gen("defense_stars", defender)
        if outcome["text"] == appearance_outcomes.homerun or outcome["text"] == appearance_outcomes.grandslam:
            runs = 1
            for base in self.bases.values():
                if base is not None:
                    runs += 1
            self.bases = {1 : None, 2 : None, 3 : None}
            return runs

        elif "advance" in outcome.keys():
            runs = 0
            if self.bases[3] is not None:
                outcome["text"] = appearance_outcomes.sacrifice
                self.get_batter().game_stats["sacrifices"] += 1 
                self.bases[3] = None
                runs = 1
            if self.bases[2] is not None:
                run_roll = random.gauss(math.erf(random_star_gen("baserunning_stars", self.bases[2])-def_stat)-.5,1.5)
                if run_roll > 0:
                    self.bases[3] = self.bases[2]
                    self.bases[2] = None
            return runs

        elif outcome["text"] == appearance_outcomes.fielderschoice:
            for base in range(3, 0, -1):
                if self.bases[base] is not None:
                    self.fc_out = self.bases[base]
                    for movebase in range(base,1,-1):
                        self.bases[movebase] = self.bases[movebase-1]
                    break
            self.bases[1] = self.get_batter()
            return 0

        elif outcome["ishit"]:
            runs = 0
            if outcome["text"] == appearance_outcomes.single:
                if self.bases[3] is not None:
                    runs += 1
                    self.bases[3] = None
                if self.bases[2] is not None:
                    run_roll = random.gauss(math.erf(random_star_gen("baserunning_stars", self.bases[2])-def_stat)-.5,1.5)
                    if run_roll > 0:
                        runs += 1
                    else:
                        self.bases[3] = self.bases[2]
                    self.bases[2] = None
                if self.bases[1] is not None:
                    if self.bases[3] is None:
                        run_roll = random.gauss(math.erf(random_star_gen("baserunning_stars", self.bases[1])-def_stat)-.5,1.5)
                        if run_roll > 0.75:
                            self.bases[3] = self.bases[1]
                        else:
                            self.bases[2] = self.bases[1]
                    else:
                        self.bases[2] = self.bases[1]
                    self.bases[1] = None

                self.bases[1] = self.get_batter()
                return runs

            elif outcome["text"] == appearance_outcomes.double:
                runs = 0
                if self.bases[3] is not None:
                    runs += 1
                    self.bases[3] = None
                if self.bases[2] is not None:
                    runs += 1
                    self.bases[2] = None
                if self.bases[1] is not None:
                    run_roll = random.gauss(math.erf(random_star_gen("baserunning_stars", self.bases[1])-def_stat)-.5,1.5)
                    if run_roll > 1:
                        runs += 1
                        self.bases[1] = None
                    else:
                        self.bases[3] = self.bases[1]
                        self.bases[1] = None
                self.bases[2] = self.get_batter()
                return runs
                    

            elif outcome["text"] == appearance_outcomes.triple:
                runs = 0
                for basenum in self.bases.keys():
                    if self.bases[basenum] is not None:
                        runs += 1
                        self.bases[basenum] = None
                self.bases[3] = self.get_batter()
                return runs


    def batterup(self):
        scores_to_add = 0
        result = self.at_bat()
        self.get_batter()
        if self.top_of_inning:
            offense_team = self.teams["away"]
            defense_team = self.teams["home"]
            defender = random.choice(self.teams["home"].lineup)
        else:
            offense_team = self.teams["home"]
            defense_team = self.teams["away"]
            defender = random.choice(self.teams["away"].lineup)

        if result["ishit"]: #if batter gets a hit:
            self.get_batter().game_stats["hits"] += 1
            self.get_pitcher().game_stats["hits_allowed"] += 1

            if result["text"] == appearance_outcomes.single:
                self.get_batter().game_stats["total_bases"] += 1               
            elif result["text"] == appearance_outcomes.double:
                self.get_batter().game_stats["total_bases"] += 2
            elif result["text"] == appearance_outcomes.triple:
                self.get_batter().game_stats["total_bases"] += 3
            elif result["text"] == appearance_outcomes.homerun or result["text"] == appearance_outcomes.grandslam:
                self.get_batter().game_stats["total_bases"] += 4
                self.get_batter().game_stats["home_runs"] += 1

            scores_to_add += self.baserunner_check(defender, result)

        else: #batter did not get a hit
            if result["text"] == appearance_outcomes.walk:
                walkers = [(0,self.get_batter())]
                for base in range(1,4):
                    if self.bases[base] == None:
                        break
                    walkers.append((base, self.bases[base]))
                for i in range(0, len(walkers)):
                    this_walker = walkers.pop()
                    if this_walker[0] == 3:
                        self.bases[3] = None
                        scores_to_add += 1
                    else:
                        self.bases[this_walker[0]+1] = this_walker[1] #this moves all consecutive baserunners one forward

                self.get_batter().game_stats["walks_taken"] += 1
                self.get_pitcher().game_stats["walks_allowed"] += 1
            
            elif result["text"] == appearance_outcomes.doubleplay:
                self.get_pitcher().game_stats["outs_pitched"] += 2
                self.outs += 2
                self.bases[1] = None

            elif result["text"] == appearance_outcomes.fielderschoice:
                self.get_pitcher().game_stats["outs_pitched"] += 1
                self.outs += 1
                scores_to_add += self.baserunner_check(defender, result)

            elif "advance" in result.keys():
                self.get_pitcher().game_stats["outs_pitched"] += 1
                self.outs += 1
                if self.bases[3] is not None:
                    self.get_batter().game_stats["sacrifices"] += 1
                scores_to_add += self.baserunner_check(defender, result)

            elif result["text"] == appearance_outcomes.strikeoutlooking or result["text"] == appearance_outcomes.strikeoutswinging:
                self.get_pitcher().game_stats["outs_pitched"] += 1
                self.outs += 1
                self.get_batter().game_stats["strikeouts_taken"] += 1
                self.get_pitcher().game_stats["strikeouts_given"] += 1

            else: 
                self.get_pitcher().game_stats["outs_pitched"] += 1
                self.outs += 1

        self.get_batter().game_stats["plate_appearances"] += 1
        
        offense_team.score += scores_to_add
        self.get_batter().game_stats["rbis"] += scores_to_add
        self.get_pitcher().game_stats["runs_allowed"] += scores_to_add
        offense_team.lineup_position += 1 #put next batter up
        if self.outs >= 3:
            self.flip_inning()
         

        return (result, scores_to_add) #returns ab information and scores

    def flip_inning(self):
        for base in self.bases.keys():
            self.bases[base] = None
        self.outs = 0
        if not self.top_of_inning:
            self.inning += 1
            if self.inning > self.max_innings and self.teams["home"].score != self.teams["away"].score: #game over
                self.over = True
        self.top_of_inning = not self.top_of_inning


    def end_of_game_report(self):
        return {
                "away_team" : self.teams["away"],
                "away_pitcher" : self.teams["away"].pitcher,
                "home_team" : self.teams["home"],
                "home_pitcher" : self.teams["home"].pitcher
            }


    def gamestate_update_full(self):   
        self.last_update = self.batterup()
        return self.gamestate_display_full()

    def gamestate_display_full(self):
        try:
            punc = ""
            if self.last_update[0]["defender"] != "":
                punc = "."
            if not self.over:
                if self.top_of_inning:
                    inningtext = "top"
                else:
                    inningtext = "bottom"

                updatestring = f"{self.last_update[0]['batter']} {self.last_update[0]['text'].value} {self.last_update[0]['defender']}{punc}\n"

                if self.last_update[1] > 0:
                    updatestring += f"{self.last_update[1]} runs scored!"

                return f"""Last update: {updatestring}

    Score: {self.teams['away'].score} - {self.teams['home'].score}.
    Current inning: {inningtext} of {self.inning}. {self.outs} outs.
    Pitcher: {self.get_pitcher().name}
    Batter: {self.get_batter().name}
    Bases: 3: {str(self.bases[3])} 2: {str(self.bases[2])} 1: {str(self.bases[1])}
    """
            else:
                return f"""Game over! Final score: **{self.teams['away'].score} - {self.teams['home'].score}**
    Last update: {self.last_update[0]['batter']} {self.last_update[0]['text'].value} {self.last_update[0]['defender']}{punc}"""
        except TypeError:
            return "Game not started."

    def add_stats(self):
        players = []
        for this_player in self.teams["away"].lineup:
            players.append((this_player.name, this_player.game_stats))
        for this_player in self.teams["home"].lineup:
            players.append((this_player.name, this_player.game_stats))
        players.append((self.teams["home"].pitcher.name, self.teams["home"].pitcher.game_stats))
        players.append((self.teams["away"].pitcher.name, self.teams["away"].pitcher.game_stats))
        db.add_stats(players)
        


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


def get_team(name):
    #try:
    team_json = jsonpickle.decode(db.get_team(name)[0], keys=True, classes=team)
    if team_json is not None:
        return team_json
    return None
   # except:
        #return None

def save_team(this_team, user_id):
    try:
        this_team.prepare_for_save()
        team_json_string = jsonpickle.encode(this_team, keys=True)
        db.save_team(this_team.name, team_json_string, user_id)
        return True
    except:
        return None

def get_all_teams():
    teams = []
    for team_pickle in db.get_all_teams():
        this_team = jsonpickle.decode(team_pickle[0], keys=True, classes=team)
        teams.append(this_team)
    return teams

def search_team(search_term):
    teams = []
    for team_pickle in db.search_teams(search_term):
        this_team = jsonpickle.decode(team_pickle[0], keys=True, classes=team)
        teams.append(this_team)
    return teams