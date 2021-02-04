import json, random, os, math, jsonpickle
from enum import Enum
import database as db

data_dir = "data"
games_config_file = os.path.join(data_dir, "games_config.json")

def config():
    if not os.path.exists(os.path.dirname(games_config_file)):
        os.makedirs(os.path.dirname(games_config_file))
    if not os.path.exists(games_config_file):
        #generate default config
        config_dic = {
                "default_length" : 3,
                "stlat_weights" : {
                        "batting_stars" : 1, #batting
                        "pitching_stars" : 0.8, #pitching
                        "baserunning_stars" : 1, #baserunning
                        "defense_stars" : 1 #defense
                    },
                "stolen_base_chance_mod" : 1,
                "stolen_base_success_mod" : 1
            }
        with open(games_config_file, "w") as config_file:
            json.dump(config_dic, config_file, indent=4)
            return config_dic
    else:
        with open(games_config_file) as config_file:
            return json.load(config_file)

def all_weathers():
    weathers_dic = {
        #"Supernova" : weather("Supernova", "🌟"),
        #"Midnight": weather("Midnight", "🕶"),
        #"Slight Tailwind": weather("Slight Tailwind", "🏌️‍♀️"),
        "Heavy Snow": weather("Heavy Snow", "❄"),
        "Twilight" : weather("Twilight", "👻"),
        "Thinned Veil" : weather("Thinned Veil", "🌌"),
        "Heat Wave" : weather("Heat Wave", "🌄"),
        "Drizzle" : weather("Drizzle", "🌧")
        }
    return weathers_dic

class appearance_outcomes(Enum):
    strikeoutlooking = "strikes out looking."
    strikeoutswinging = "strikes out swinging."
    groundout = "grounds out to"
    flyout = "flies out to"
    fielderschoice = "reaches on fielder's choice. {} is out at {} base." #requires .format(player, base_string)
    doubleplay = "grounds into a double play!"
    sacrifice = "hits a sacrifice fly towards"
    walk = "draws a walk."
    single = "hits a single!"
    double = "hits a double!"
    triple = "hits a triple!"
    homerun = "hits a dinger!"
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
        self.rotation = []
        self.pitcher = None
        self.score = 0
        self.slogan = None

    def find_player(self, name):
        for index in range(0,len(self.lineup)):
            if self.lineup[index].name == name:
                return (self.lineup[index], index, self.lineup)
        for index in range(0,len(self.rotation)):
            if self.rotation[index].name == name:
                return (self.rotation[index], index, self.rotation)
        else:
            return (None, None, None)

    def find_player_spec(self, name, roster):
         for s_index in range(0,len(roster)):
            if roster[s_index].name == name:
                return (roster[s_index], s_index)

    def average_stars(self):
        total_stars = 0
        for _player in self.lineup:
            total_stars += _player.stlats["batting_stars"]
        for _player in self.rotation:
            total_stars += _player.stlats["pitching_stars"]
        return total_stars/(len(self.lineup) + len(self.rotation))

    def swap_player(self, name):
        this_player, index, roster = self.find_player(name)
        if this_player is not None and len(roster) > 1:
            if roster == self.lineup:
                if self.add_pitcher(this_player):
                    roster.pop(index)
                    return True
            else:
                if self.add_lineup(this_player)[0]:
                    self.rotation.pop(index)
                    return True
        return False

    def delete_player(self, name):
        this_player, index, roster = self.find_player(name)
        if this_player is not None and len(roster) > 1:
            roster.pop(index)
            return True
        else:
            return False

    def slide_player(self, name, new_spot):
        this_player, index, roster = self.find_player(name)
        if this_player is not None and new_spot <= len(roster):
            roster.pop(index)
            roster.insert(new_spot-1, this_player)
            return True
        else:
            return False

    def slide_player_spec(self, this_player_name, new_spot, roster):
        index = None
        for s_index in range(0,len(roster)):
            if roster[s_index].name == this_player_name:
                index = s_index
                this_player = roster[s_index]
        if index is None:
            return False
        elif new_spot <= len(roster):
            roster.pop(index)
            roster.insert(new_spot-1, this_player)
            return True
        else:
            return False
                
    def add_lineup(self, new_player):
        if len(self.lineup) < 20:
            self.lineup.append(new_player)
            return (True,)
        else:
            return (False, "20 players in the lineup, maximum. We're being really generous here.")
    
    def add_pitcher(self, new_player):
        if len(self.rotation) < 8:
            self.rotation.append(new_player)
            return True
        else:
            return False

    def set_pitcher(self, rotation_slot = None, use_lineup = False):
        temp_rotation = self.rotation.copy()
        if use_lineup:         
            for batter in self.lineup:
                temp_rotation.append(batter)
        if rotation_slot is None:
            self.pitcher = random.choice(temp_rotation)
        else:
            self.pitcher = temp_rotation[(rotation_slot-1) % len(temp_rotation)]

    def is_ready(self):
        try:
            return (len(self.lineup) >= 1 and len(self.rotation) > 0)
        except AttributeError:
            self.rotation = [self.pitcher]
            self.pitcher = None
            return (len(self.lineup) >= 1 and len(self.rotation) > 0)

    def prepare_for_save(self):
        self.lineup_position = 0
        self.score = 0
        if self.pitcher is not None and self.pitcher not in self.rotation:
            self.rotation.append(self.pitcher)
        self.pitcher = None
        for this_player in self.lineup:
            for stat in this_player.game_stats.keys():
                this_player.game_stats[stat] = 0
        for this_player in self.rotation:
            for stat in this_player.game_stats.keys():
                this_player.game_stats[stat] = 0
        return self

    def finalize(self):
        if self.is_ready():
            if self.pitcher == None:
                self.set_pitcher()
            while len(self.lineup) <= 4:
                self.lineup.append(random.choice(self.lineup))       
            return self
        else:
            return False


class game(object):

    def __init__(self, team1, team2, length=None):
        self.over = False
        self.teams = {"away" : team1, "home" : team2}
        self.inning = 1
        self.outs = 0
        self.top_of_inning = True
        self.last_update = ({},0) #this is a ({outcome}, runs) tuple
        self.owner = None
        self.ready = False
        self.victory_lap = False
        if length is not None:
            self.max_innings = length
        else:
            self.max_innings = config()["default_length"]
        self.bases = {1 : None, 2 : None, 3 : None}
        self.weather = weather("Sunny","🌞")

    def get_batter(self):
        if self.top_of_inning:
            bat_team = self.teams["away"]
            counter = self.weather.counter_away
        else:
            bat_team = self.teams["home"]
            counter = self.weather.counter_home

        if self.weather.name == "Heavy Snow" and counter == bat_team.lineup_position:
            return bat_team.pitcher
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
            defender_list = self.teams["home"].lineup.copy()
        else:
            defender_list = self.teams["away"].lineup.copy()

        defender_list.append(pitcher)
        defender = random.choice(defender_list) #make pitchers field

        outcome["batter"] = batter
        outcome["defender"] = ""

        bat_stat = random_star_gen("batting_stars", batter)
        pitch_stat = random_star_gen("pitching_stars", pitcher)
        if weather.name == "Supernova":
            pitch_stat = pitch_stat * 0.9

        pb_system_stat = (random.gauss(1*math.erf((bat_stat - pitch_stat)*1.5)-1.8,2.2))
        hitnum = random.gauss(2*math.erf(bat_stat/4)-1,3)

        if self.weather.name == "Twilight":
            error_line = - (math.log(defender.stlats["defense_stars"] + 1)/50) + 1
            error_roll = random.random()
            if error_roll > error_line:
                outcome["error"] = True
                outcome["defender"] = defender
                pb_system_stat = 0.1

        
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

            if self.bases[1] is not None and hitnum < -2 and self.outs != 2:
                outcome["text"] = appearance_outcomes.doubleplay
                outcome["defender"] = ""

            #for base in self.bases.values():
                #if base is not None:
                    #fc_flag = True

            runners = [(0,self.get_batter())]
            for base in range(1,4):
                if self.bases[base] == None:
                    break
                runners.append((base, self.bases[base]))
            outcome["runners"] = runners #list of consecutive baserunners: (base number, player object)

            if self.outs < 2 and len(runners) > 1: #fielder's choice replaces not great groundouts if any forceouts are present
                def_stat = random_star_gen("defense_stars", defender)
                if -1.5 <= hitnum and hitnum < -0.5: #poorly hit groundouts
                    outcome["text"] = appearance_outcomes.fielderschoice
                    outcome["defender"] = ""
            
            if 2.5 <= hitnum and self.outs < 2: #well hit flyouts can lead to sacrifice flies/advanced runners
                if self.bases[2] is not None or self.bases[3] is not None:
                    outcome["advance"] = True
        else:
            outcome["ishit"] = True
            if hitnum < 1:
                outcome["text"] = appearance_outcomes.single
            elif hitnum < 2.85 or "error" in outcome.keys():
                outcome["text"] = appearance_outcomes.double
            elif hitnum < 3.1:
                outcome["text"] = appearance_outcomes.triple
            else:
                if self.bases[1] is not None and self.bases[2] is not None and self.bases[3] is not None:
                    outcome["text"] = appearance_outcomes.grandslam
                else:
                    outcome["text"] = appearance_outcomes.homerun
        return outcome

    def thievery_attempts(self): #returns either false or "at-bat" outcome
        thieves = []
        attempts = []
        for base in self.bases.keys():
            if self.bases[base] is not None and base != 3: #no stealing home in simsim, sorry stu
                if self.bases[base+1] is None: #if there's somewhere to go
                    thieves.append((self.bases[base], base))
        for baserunner, start_base in thieves:
            run_stars = random_star_gen("baserunning_stars", baserunner)*config()["stolen_base_chance_mod"]
            if self.weather.name == "Midnight":
                run_stars = run_stars*2
            def_stars = random_star_gen("defense_stars", self.get_pitcher())
            if run_stars >= (def_stars - 1.5): #if baserunner isn't worse than pitcher
                roll = random.random()
                if roll >= (-(((run_stars+1)/14)**2)+1): #plug it into desmos or something, you'll see
                    attempts.append((baserunner, start_base))

        if len(attempts) == 0:
            return False
        else:     
            return (self.steals_check(attempts), 0) #effectively an at-bat outcome with no score

    def steals_check(self, attempts):
        if self.top_of_inning:
            defense_team = self.teams["home"]
        else:
            defense_team = self.teams["away"]

        outcome = {}
        outcome["steals"] = []

        for baserunner, start_base in attempts:
            defender = random.choice(defense_team.lineup) #excludes pitcher
            run_stat = random_star_gen("baserunning_stars", baserunner)
            def_stat = random_star_gen("defense_stars", defender)
            run_roll = random.gauss(2*math.erf((run_stat-def_stat)/4)-1,3)*config()["stolen_base_success_mod"]
            if start_base == 2:
                run_roll = run_roll * .9 #stealing third is harder
            if run_roll < 1:
                outcome["steals"].append(f"{baserunner} was caught stealing {base_string(start_base+1)} base by {defender}!")
                self.get_pitcher().game_stats["outs_pitched"] += 1
                self.outs += 1
            else:
                outcome["steals"].append(f"{baserunner} steals {base_string(start_base+1)} base!")
                self.bases[start_base+1] = baserunner
            self.bases[start_base] = None

        if self.outs >= 3:
            self.flip_inning()

        return outcome

    def baserunner_check(self, defender, outcome):
        def_stat = random_star_gen("defense_stars", defender)
        if outcome["text"] == appearance_outcomes.homerun or outcome["text"] == appearance_outcomes.grandslam:
            runs = 1
            for base in self.bases.values():
                if base is not None:
                    runs += 1
            self.bases = {1 : None, 2 : None, 3 : None}
            if "veil" in outcome.keys():
                if runs < 4:
                    self.bases[runs] = self.get_batter()
                else:
                    runs += 1
            return runs

        elif "advance" in outcome.keys():
            runs = 0
            if self.bases[3] is not None:
                outcome["text"] = appearance_outcomes.sacrifice
                self.get_batter().game_stats["sacrifices"] += 1 
                self.bases[3] = None
                runs = 1
            if self.bases[2] is not None:
                run_roll = random.gauss(2*math.erf((random_star_gen("baserunning_stars", self.bases[2])-def_stat)/4)-1,3)
                if run_roll > 2:
                    self.bases[3] = self.bases[2]
                    self.bases[2] = None
            return runs

        elif outcome["text"] == appearance_outcomes.fielderschoice:
            furthest_base, runner = outcome["runners"].pop() #get furthest baserunner
            self.bases[furthest_base] = None 
            outcome["fc_out"] = (runner.name, base_string(furthest_base+1)) #runner thrown out
            for index in range(0,len(outcome["runners"])):
                base, this_runner = outcome["runners"].pop()
                self.bases[base+1] = this_runner #includes batter, at base 0
            if self.bases[3] is not None and furthest_base == 1: #fielders' choice with runners on the corners
                self.bases[3] = None
                return 1
            return 0

        elif outcome["text"] == appearance_outcomes.groundout or outcome["text"] == appearance_outcomes.doubleplay:
            runs = 0
            if self.bases[3] is not None:
                runs += 1
                self.bases[3] = None
            if self.bases[2] is not None:
                run_roll = random.gauss(2*math.erf((random_star_gen("baserunning_stars", self.bases[2])-def_stat)/4)-1,3)
                if run_roll > 1.5 or outcome["text"] == appearance_outcomes.doubleplay: #double play gives them time to run, guaranteed
                    self.bases[3] = self.bases[2]
                    self.bases[2] = None
            if self.bases[1] is not None: #double plays set this to None before this call
                run_roll = random.gauss(2*math.erf((random_star_gen("baserunning_stars", self.bases[1])-def_stat)/4)-1,3)
                if run_roll < 2 or self.bases[2] is not None: #if runner can't make it or if baserunner blocking on second, convert to fielder's choice
                    outcome["text"] == appearance_outcomes.fielderschoice
                    runners = [(0,self.get_batter())]
                    for base in range(1,4):
                        if self.bases[base] == None:
                            break
                        runners.append((base, self.bases[base]))
                    outcome["runners"] = runners #rebuild consecutive runners
                    return runs + self.baserunner_check(defender, outcome) #run again as fielder's choice instead
                else:
                    self.bases[2] = self.bases[1]
                    self.bases[1] = None
            return runs

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
        if self.top_of_inning:
            offense_team = self.teams["away"]
            weather_count = self.weather.counter_away
            defense_team = self.teams["home"]
        else:
            offense_team = self.teams["home"]
            weather_count = self.weather.counter_home
            defense_team = self.teams["away"]

        if self.weather.name == "Slight Tailwind" and "mulligan" not in self.last_update[0].keys() and not result["ishit"] and result["text"] != appearance_outcomes.walk: 
            mulligan_roll_target = -((((self.get_batter().stlats["batting_stars"])-5)/6)**2)+1
            if random.random() > mulligan_roll_target and self.get_batter().stlats["batting_stars"] <= 5:
                result["mulligan"] = True
                return (result, 0)

        if self.weather.name == "Heavy Snow" and weather_count == offense_team.lineup_position and "snow_atbat" not in self.last_update[0].keys():
            result["snow_atbat"] = True
            result["text"] = f"{offense_team.lineup[offense_team.lineup_position % len(offense_team.lineup)].name}'s hands are too cold! {self.get_batter().name} is forced to bat!"
            return (result, 0)

        defenders = defense_team.lineup.copy()
        defenders.append(defense_team.pitcher)
        defender = random.choice(defenders) #pitcher can field outs now :3

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
                if self.weather.name == "Thinned Veil":
                    result["veil"] = True



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
                if self.outs < 3:
                    scores_to_add += self.baserunner_check(defender, result)
                    self.get_batter().game_stats["rbis"] -= scores_to_add #remove the fake rbi from the player in advance

            elif result["text"] == appearance_outcomes.fielderschoice or result["text"] == appearance_outcomes.groundout:
                self.get_pitcher().game_stats["outs_pitched"] += 1
                self.outs += 1
                if self.outs < 3:
                    scores_to_add += self.baserunner_check(defender, result)

            elif "advance" in result.keys():
                self.get_pitcher().game_stats["outs_pitched"] += 1
                self.outs += 1
                if self.outs < 3:
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
        
        if self.outs < 3:
            offense_team.score += scores_to_add #only add points if inning isn't over
        else:
            scores_to_add = 0
        self.get_batter().game_stats["rbis"] += scores_to_add
        self.get_pitcher().game_stats["runs_allowed"] += scores_to_add
        offense_team.lineup_position += 1 #put next batter up
        if self.outs >= 3:
            self.flip_inning()
            if self.weather.name == "Heat Wave":
                if self.top_of_inning:
                    self.weather.home_pitcher = self.get_pitcher()
                    if self.inning >= self.weather.counter_home:
                        self.weather.counter_home = self.weather.counter_home - (self.weather.counter_home % 5) + 5 + random.randint(1,4) #rounds down to last 5, adds up to next 5. then adds a random number 2<=x<=5 to determine next pitcher                       
                        tries = 0
                        while self.get_pitcher() == self.weather.home_pitcher and tries < 3:
                            self.teams["home"].set_pitcher(use_lineup = True)
                            tries += 1

 
                else:
                    self.weather.away_pitcher = self.get_pitcher()
                    if self.inning >= self.weather.counter_away:
                        self.weather.counter_away = self.weather.counter_away - (self.weather.counter_away % 5) + 5 + random.randint(1,4)                  
                        tries = 0
                        while self.get_pitcher() == self.weather.away_pitcher and tries < 3:
                            self.teams["away"].set_pitcher(use_lineup = True)
                            tries += 1
         

        return (result, scores_to_add) #returns ab information and scores

    def flip_inning(self):
        for base in self.bases.keys():
            self.bases[base] = None
        self.outs = 0
        if self.top_of_inning and self.weather.name == "Heavy Snow" and self.weather.counter_away < self.teams["away"].lineup_position:
            self.weather.counter_away = self.pitcher_insert(self.teams["away"])

        if not self.top_of_inning:
            if self.weather.name == "Heavy Snow" and self.weather.counter_home < self.teams["home"].lineup_position:
                self.weather.counter_home = self.pitcher_insert(self.teams["home"])
            self.inning += 1
            if self.inning > self.max_innings and self.teams["home"].score != self.teams["away"].score: #game over
                self.over = True
        self.top_of_inning = not self.top_of_inning

        if self.weather.name == "Drizzle":
            if self.top_of_inning:
                self.bases[2] = self.teams["away"].lineup[(self.teams["away"].lineup_position-1) % len(self.teams["away"].lineup)]
            else:
                self.bases[2] = self.teams["home"].lineup[(self.teams["home"].lineup_position-1) % len(self.teams["home"].lineup)]

    def pitcher_insert(self, this_team):
        rounds = math.ceil(this_team.lineup_position / len(this_team.lineup))
        position = random.randint(0, len(this_team.lineup)-1)
        return rounds * len(this_team.lineup) + position

    def end_of_game_report(self):
        return {
                "away_team" : self.teams["away"],
                "away_pitcher" : self.teams["away"].pitcher,
                "home_team" : self.teams["home"],
                "home_pitcher" : self.teams["home"].pitcher
            }

    def named_bases(self):
        name_bases = {}
        for base in range(1,4):
            if self.bases[base] is not None:
                name_bases[base] = self.bases[base].name
            else:
                name_bases[base] = None

        return name_bases


    def gamestate_update_full(self):
        attempts = self.thievery_attempts()
        if attempts == False:
            self.last_update = self.batterup()
        else:
            self.last_update = attempts
        return self.gamestate_display_full()

    def gamestate_display_full(self):
        if "steals" in self.last_update[0].keys():
            return "Still in progress."
        else:
            try:
                punc = ""
                if self.last_update[0]["defender"] != "":
                    punc = "."
                if not self.over:
                    if self.top_of_inning:
                        inningtext = "top"
                    else:
                        inningtext = "bottom"

                    updatestring = "this isn't used but i don't want to break anything"

                    return "this isn't used but i don't want to break anything"
                else:
                    return f"""Game over! Final score: **{self.teams['away'].score} - {self.teams['home'].score}**
        Last update: {self.last_update[0]['batter']} {self.last_update[0]['text'].value} {self.last_update[0]['defender']}{punc}"""
            except TypeError:
                return "Game not started."
            except KeyError:
                return "Game not started."

    def add_stats(self):
        players = self.get_stats()
        db.add_stats(players)

    def get_stats(self):
        players = []
        for this_player in self.teams["away"].lineup:
            players.append((this_player.name, this_player.game_stats))
        for this_player in self.teams["home"].lineup:
            players.append((this_player.name, this_player.game_stats))
        players.append((self.teams["home"].pitcher.name, self.teams["home"].pitcher.game_stats))
        players.append((self.teams["away"].pitcher.name, self.teams["away"].pitcher.game_stats))
        return players

    def get_team_specific_stats(self):
        players = {
            self.teams["away"].name : [],
            self.teams["home"].name : []
            }
        for this_player in self.teams["away"].lineup:
            players[self.teams["away"].name].append((this_player.name, this_player.game_stats))
        for this_player in self.teams["home"].lineup:
            players[self.teams["home"].name].append((this_player.name, this_player.game_stats))
        players[self.teams["home"].name].append((self.teams["home"].pitcher.name, self.teams["home"].pitcher.game_stats))
        players[self.teams["away"].name].append((self.teams["away"].pitcher.name, self.teams["away"].pitcher.game_stats))
        return players
        


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
    try:
        team_json = jsonpickle.decode(db.get_team(name)[0], keys=True, classes=team)
        if team_json is not None:
            if team_json.pitcher is not None: #detects old-format teams, adds pitcher
                team_json.rotation.append(team_json.pitcher)
                team_json.pitcher = None
                update_team(team_json)
            return team_json
        return None
    except AttributeError:
        team_json.rotation = []
        team_json.rotation.append(team_json.pitcher)
        team_json.pitcher = None
        update_team(team_json)
        return team_json
    except:
        return None

def get_team_and_owner(name):
    try:
        counter, name, team_json_string, timestamp, owner_id = db.get_team(name, owner=True)
        team_json = jsonpickle.decode(team_json_string, keys=True, classes=team)
        if team_json is not None:
            if team_json.pitcher is not None: #detects old-format teams, adds pitcher
                team_json.rotation.append(team_json.pitcher)
                team_json.pitcher = None
                update_team(team_json)
            return (team_json, owner_id)
        return None
    except AttributeError:
        team_json.rotation = []
        team_json.rotation.append(team_json.pitcher)
        team_json.pitcher = None
        update_team(team_json)
        return (team_json, owner_id)
    except:
        return None

def save_team(this_team, user_id):
    try:
        this_team.prepare_for_save()
        team_json_string = jsonpickle.encode(this_team, keys=True)
        db.save_team(this_team.name, team_json_string, user_id)
        return True
    except:
        return None

def update_team(this_team):
    try:
        this_team.prepare_for_save()
        team_json_string = jsonpickle.encode(this_team, keys=True)
        db.update_team(this_team.name, team_json_string)
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
        team_json = jsonpickle.decode(team_pickle[0], keys=True, classes=team)
        try:         
            if team_json.pitcher is not None:
                if len(team_json.rotation) == 0: #detects old-format teams, adds pitcher
                    team_json.rotation.append(team_json.pitcher)
                    team_json.pitcher = None
                    update_team(team_json)
        except AttributeError:
            team_json.rotation = []
            team_json.rotation.append(team_json.pitcher)
            team_json.pitcher = None
            update_team(team_json)
        except:
            return None

        teams.append(team_json)
    return teams

def base_string(base):
    if base == 1:
        return "first"
    elif base == 2:
        return "second"
    elif base == 3:
        return "third"
    elif base == 4:
        return "None"

class weather(object):
    name = "Sunny"
    emoji = "🌞"

    def __init__(self, new_name, new_emoji):
        self.name = new_name
        self.emoji = new_emoji
        self.counter_away = 0
        self.counter_home = 0

    def __str__(self):
        return f"{self.emoji} {self.name}"
