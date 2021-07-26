import random, math, roman
from gametext import appearance_outcomes, game_strings_base, base_string

class Weather:
    name = "Sunny"
    emoji = "🌞"
    duration_range = [3,5]

    def __init__(self, game):
        pass    

    def __str__(self):
        return f"{self.emoji} {self.name}"

    def set_duration(self):
        pass

    def modify_atbat_stats(self, player_rolls):
        # Activates before batting
        pass

    def modify_steal_stats(self, roll):
        pass

    def modify_atbat_roll(self, outcome, roll, defender):
        # activates after batter roll
        pass

    def activate(self, game, result):
        # activates after the batter calculation. modify result, or just return another thing
        pass
    
    def steal_activate(self, game, result):
        pass

    def steal_post_activate(self, game, result):
        pass

    def post_activate(self, game, result):
        pass

    def on_choose_next_batter(self, game):
        pass

    def on_flip_inning(self, game):
        pass

    def modify_top_of_inning_message(self, game, state):
        pass

    def modify_atbat_message(self, game, state):
        pass

    def modify_gamestate(self, game, state):
        pass

    def modify_game_end_message(self, game, state):
        pass

    def weather_report(self, game, state):
        game.weather = random.choice(list(safe_weathers().values()))(game)
        state["update_emoji"] = "🚌"
        state["update_text"] += f" Weather report: {game.weather.name} {game.weather.emoji}"


class Supernova(Weather):
    name = "Supernova"
    emoji = "🌟"
    duration_range = [1,2]

    def modify_atbat_stats(self, roll):
        roll["pitch_stat"] *= 0.8

class Midnight(Weather):
    name = "Midnight"
    emoji = "🕶"
    duration_range = [1,1]

    def modify_steal_stats(self, roll):
        roll["run_stars"] *= 2

class SlightTailwind(Weather):
    name = "Slight Tailwind"
    emoji = "🏌️‍♀️"
    duration_range = [1,2]

    def activate(self, game, result):

        if "mulligan" not in game.last_update[0].keys() and not result["ishit"] and result["outcome"] != appearance_outcomes.walk: 
            mulligan_roll_target = -((((game.get_batter().stlats["batting_stars"])-5)/6)**2)+1
            if random.random() > mulligan_roll_target and game.get_batter().stlats["batting_stars"] <= 5:
                result.clear()
                result.update({
                    "text": f"{game.get_batter()} would have gone out, but they took a mulligan!",
                    "mulligan": True,
                    "text_only": True,
                    "weather_message": True,
                })

class Starlight(Weather):
    name = "Starlight"
    emoji = "🌃"
    duration_range = [2,2]

    def activate(self, game, result):

        if (result["outcome"] == appearance_outcomes.homerun or result["outcome"] == appearance_outcomes.grandslam):
            result["weather_message"] = True
            dinger_roll = random.random()
            if "dragon" in game.get_batter().name.lower():
                result["dragin_the_park"] = True

            elif dinger_roll < 0.941:
                result.clear()
                result.update({
                    "text": f"{game.get_batter()} hits a dinger, but the stars do not approve! The ball pulls foul.",
                    "text_only": True,
                    "weather_message": True
                })
            else:
                result["in_the_park"] = True


    def modify_atbat_message(self, game, state):
        result = game.last_update[0]
        if "in_the_park" in result.keys():
            state["update_text"] = f"The stars are pleased with {result['batter']}, and allow a dinger! {game.last_update[1]} runs scored!"
        elif "dragin_the_park" in result.keys():
            state["update_text"] = f"The stars enjoy watching dragons play baseball, and allow {result['batter']} to hit a dinger! {game.last_update[1]} runs scored!"
               

class Blizzard(Weather):
    name = "Blizzard"
    emoji = "❄"
    duration_range = [2,3]

    def __init__(self, game):
        self.counter_away = random.randint(0,len(game.teams['away'].lineup)-1)
        self.counter_home = random.randint(0,len(game.teams['home'].lineup)-1)

        self.swapped_batter_data = None

    def activate(self, game, result):        
        if self.swapped_batter_data:
            original, sub = self.swapped_batter_data
            self.swapped_batter_data = None
            result.clear()
            result.update({
                "snow_atbat": True,
                "text": f"{original.name}'s hands are too cold! {sub.name} is forced to bat!",
                "text_only": True,
                "weather_message": True,
            })

    def on_flip_inning(self, game):
        if game.top_of_inning and self.counter_away < game.teams["away"].lineup_position:
            self.counter_away = self.pitcher_insert_index(game.teams["away"])

        if not game.top_of_inning and self.counter_home < game.teams["home"].lineup_position:
            self.counter_home = self.pitcher_insert_index(game.teams["home"])

    def pitcher_insert_index(self, this_team):
        rounds = math.ceil(this_team.lineup_position / len(this_team.lineup))
        position = random.randint(0, len(this_team.lineup)-1)
        return rounds * len(this_team.lineup) + position

    def on_choose_next_batter(self, game):
        if game.top_of_inning:
            bat_team = game.teams["away"]
            counter = self.counter_away
        else:
            bat_team = game.teams["home"]
            counter = self.counter_home

        if bat_team.lineup_position == counter:
            self.swapped_batter_data = (game.current_batter, bat_team.pitcher) # store this to generate the message during activate()
            game.current_batter = bat_team.pitcher

class Twilight(Weather):
    name = "Twilight"
    emoji = "👻"
    duration_range = [2,3]

    def modify_atbat_roll(self, outcome, roll, defender):
        error_line = - (math.log(defender.stlats["defense_stars"] + 1)/50) + 1
        error_roll = random.random()
        if error_roll > error_line:
            outcome["error"] = True
            outcome["weather_message"] = True
            outcome["defender"] = defender
            roll["pb_system_stat"] = 0.1

    def modify_atbat_message(self, this_game, state):
        result = this_game.last_update[0]
        if "error" in result.keys():
            state["update_text"] = f"{result['batter']}'s hit goes ethereal, and {result['defender']} can't catch it! {result['batter']} reaches base safely."
            if this_game.last_update[1] > 0:
                state["update_text"] += f" {this_game.last_update[1]} runs scored!"

class ThinnedVeil(Weather):
    name = "Thinned Veil"
    emoji = "🌌"
    duration_range = [1,3]

    def activate(self, game, result):
        if result["ishit"]:
           if result["outcome"] == appearance_outcomes.homerun or result["outcome"] == appearance_outcomes.grandslam:
                result["veil"] = True

    def modify_atbat_message(self, game, state):
        if "veil" in game.last_update[0].keys():
            state["update_emoji"] = self.emoji    
            state["update_text"] += f" {game.last_update[0]['batter']}'s will manifests on {base_string(game.last_update[1])} base."

class HeatWave(Weather):
    name = "Heat Wave"
    emoji = "🌄"
    duration_range = [2,3]

    def __init__(self,game):
        self.counter_away = random.randint(2,4)
        self.counter_home = random.randint(2,4)

        self.swapped_pitcher_data = None

    def on_flip_inning(self, game):
        original_pitcher = game.get_pitcher()
        if game.top_of_inning:
            bat_team = game.teams["home"]
            counter = self.counter_home
        else:
            bat_team = game.teams["away"]
            counter = self.counter_away

        if game.inning == counter:
            if game.top_of_inning:
                self.counter_home = self.counter_home - (self.counter_home % 5) + 5 + random.randint(1,4) #rounds down to last 5, adds up to next 5. then adds a random number 2<=x<=5 to determine next pitcher                       
            else:
                self.counter_away = self.counter_away - (self.counter_away % 5) + 5 + random.randint(1,4)      

            #swap, accounting for teams where where someone's both batter and pitcher
            tries = 0
            while game.get_pitcher() == original_pitcher and tries < 3:
                bat_team.set_pitcher(use_lineup = True)
                tries += 1
            if game.get_pitcher() != original_pitcher:
                self.swapped_pitcher_data = (original_pitcher, game.get_pitcher())

    def modify_top_of_inning_message(self, game, state):
        if self.swapped_pitcher_data:
            original, sub = self.swapped_pitcher_data
            self.swapped_pitcher_data = None
            state["update_emoji"] = self.emoji
            state["update_text"] += f' {original} is exhausted from the heat. {sub} is forced to pitch!'
             
                

class Drizzle(Weather):
    name = "Drizzle"
    emoji = "🌧"
    duration_range = [2,3]

    def on_flip_inning(self, game):
        if game.top_of_inning:
            next_team = "away"
        else:
            next_team = "home"

        lineup = game.teams[next_team].lineup
        game.bases[2] = lineup[(game.teams[next_team].lineup_position-1) % len(lineup)]

    def modify_top_of_inning_message(self, game, state):
        if game.top_of_inning:
            next_team = "away"
        else:
            next_team = "home"

        placed_player = game.teams[next_team].lineup[(game.teams[next_team].lineup_position-1) % len(game.teams[next_team].lineup)]

        state["update_emoji"] = self.emoji
        state["update_text"] += f' Due to inclement weather, {placed_player.name} is placed on second base.'

class Breezy(Weather):
    name = "Breezy"
    emoji = "🎐"
    duration_range = [1,3]

    def __init__(self, game):       
        self.activation_chance = 0.08

    def activate(self, game, result):
        if random.random() < self.activation_chance:
            teamtype = random.choice(["away","home"])
            team = game.teams[teamtype]
            player = random.choice(team.lineup)
            player.stlats["batting_stars"] = player.stlats["pitching_stars"]
            player.stlats["pitching_stars"] = player.stlats["baserunning_stars"]
            old_player_name = player.name

            if not hasattr(player, "stat_name"):
                player.stat_name = old_player_name

            if ' ' in player.name:
                names = player.name.split(" ")
                try:
                    first_first_letter = names[0][0]
                    last_first_letter = names[-1][0]
                    names[0] = last_first_letter + names[0][1:]
                    names[-1] = first_first_letter + names[-1][1:]
                    player.name = ' '.join(names)
                except:
                    first_letter = player.name[0]
                    last_letter = player.name[-1]
                    player.name = last_letter + player.name[1:-1] + first_letter
            else:
                #name is one word, so turn 'bartholemew' into 'martholemeb'
                first_letter = player.name[0]
                last_letter = player.name[-1]
                player.name = last_letter + player.name[1:-1] + first_letter

            book_adjectives = ["action-packed", "historical", "mystery", "thriller", "horror", "sci-fi", "fantasy", "spooky","romantic"]
            book_types = ["novel", "novella", "poem", "anthology", "fan fiction", "autobiography"]
            book = "{} {}".format(random.choice(book_adjectives),random.choice(book_types))

            result.clear()
            result.update({
                "text": "{} stopped to enjoy a {} in the nice breeze! {} is now {}!".format(old_player_name, book, old_player_name, player.name),
                "text_only": True,
                "weather_message": True
            })

class MeteorShower(Weather):
    name = "Meteor Shower"
    emoji = "🌠"
    duration_range = [1,3]

    def __init__(self, game):
        self.activation_chance = 0.13

    def activate(self, game, result):
        if random.random() < self.activation_chance and game.occupied_bases() != {}:
            base, runner = random.choice(list(game.occupied_bases().items()))
            runner = game.bases[base]
            game.bases[base] = None

            if game.top_of_inning:
                bat_team = game.teams["away"]
            else:
                bat_team = game.teams["home"]

            bat_team.score += 1
            result.clear()
            result.update({
                    "text": f"{runner.name} wished upon one of the shooting stars, and was warped to None base!! 1 runs scored!",
                    "text_only": True,
                    "weather_message": True
                })

class Hurricane(Weather):
    name = "Hurricane"
    emoji = "🌀"
    duration_range = [1,1]

    def __init__(self, game):
        self.swaplength = random.randint(2,4)
        self.swapped = False

    def on_flip_inning(self, game):
        if game.top_of_inning and (game.inning % self.swaplength) == 0:
            self.swaplength = random.randint(2,4)
            self.swapped = True

    def modify_top_of_inning_message(self, game, state):
        if self.swapped:
            game.teams["home"].score, game.teams["away"].score = (game.teams["away"].score, game.teams["home"].score) #swap scores
            state["away_score"], state["home_score"] = (game.teams["away"].score, game.teams["home"].score)
            state["update_emoji"] = self.emoji
            state["update_text"] += " The hurricane rages on, flipping the scoreboard!"
            self.swapped = False

class Tornado(Weather):
    name = "Tornado"
    emoji = "🌪"
    duration_range = [1,2]

    def __init__(self, game):
        self.activation_chance = 0.33
        self.counter = 0

    def activate(self, game, result):
        if self.counter == 0 and random.random() < self.activation_chance and game.occupied_bases() != {}:
            runners = list(game.bases.values())
            current_runners = runners.copy()
            self.counter = 5
            while runners == current_runners and self.counter > 0:
                random.shuffle(runners)
                self.counter -= 1
            for index in range(1,4):
                game.bases[index] = runners[index-1]

            result.clear()
            result.update({
                    "text": f"The tornado sweeps across the field and pushes {'the runners' if len(game.occupied_bases().values())>1 else list(game.occupied_bases().values())[0].name} to a different base!",
                    "text_only": True,
                    "weather_message": True
                })
            self.counter = 2

        elif self.counter > 0:
            self.counter -= 1
            


class Downpour(Weather):
    name = "Torrential Downpour"
    emoji = '⛈'
    duration_range = [1,1]

    def __init__(self, game):
        self.target = game.max_innings
        self.name = f"Torrential Downpour: {roman.roman_convert(str(self.target))}"
        self.emoji = '⛈'
        

    def on_flip_inning(self, game):
        high_score = game.teams["home"].score if game.teams["home"].score > game.teams["away"].score else game.teams["away"].score
        if high_score >= self.target and game.teams["home"].score != game.teams["away"].score:
            game.max_innings = game.inning
        else:
            game.max_innings = game.inning + 1

    def modify_gamestate(self, game, state):
        state["max_innings"] = "∞"

    def modify_top_of_inning_message(self, game, state):
        state["update_emoji"] = self.emoji
        if game.teams["away"].score >= self.target: #if the away team has met the target
            if game.teams["home"].score == game.teams["away"].score: #if the teams are tied
                state["update_text"] = "The gods demand a victor. Play on."
            else:
                state["update_text"] = f"The gods are pleased, but demand more from {game.teams['home'].name}. Take the field."
        else:
            state["update_text"] = "The gods are not yet pleased. Play continues through the storm."

    def modify_game_end_message(self, game, state):
        state["update_emoji"] = self.emoji
        state["update_text"] = f"{self.target} runs are reached, pleasing the gods. The storm clears."

class SummerMist(Weather):
    name = "Summer Mist"
    emoji = "🌁"
    duration_range = [1,3]
    substances = ["yellow mustard", "cat fur", "dread", "caramel", "nacho cheese", "mud", "dirt", "justice", "a green goo", "water, probably", "antimatter", "something not of this world", "live ferrets", "snow", "leaves",
                 "yarn", "seaweed", "sawdust", "stardust", "code fragments", "milk", "lizards", "a large tarp", "feathers"]

    def __init__(self, game):
        self.missing_players = {game.teams["home"].name: None, game.teams["away"].name: None}
        self.text = ""

    def activate(self, game, result):
        if result["outcome"] in [appearance_outcomes.flyout, appearance_outcomes.groundout, appearance_outcomes.sacrifice]:
            roll = random.random()
            if roll < .4: #get lost
                result["mist"] = True
                self.text = f" {result['batter'].name} gets lost in the mist on the way back to the dugout."
                if self.missing_players[result["offense_team"].name] is not None:
                    self.text += f" {self.missing_players[result['offense_team'].name].name} wanders back, covered in {random.choice(self.substances)}!"
                    result["offense_team"].lineup[result["offense_team"].lineup_position % len(result["offense_team"].lineup)] = self.missing_players[result["offense_team"].name]
                else:
                    result["offense_team"].lineup.pop(result["offense_team"].lineup_position % len(result["offense_team"].lineup))
                self.missing_players[result["offense_team"].name] = result["batter"]

    def modify_atbat_message(self, game, state):
        if "mist" in game.last_update[0]:
            state["update_emoji"] = self.emoji
            state["update_text"] += self.text
            self.text = ""

class LeafEddies(Weather):
    name = "Leaf Eddies"
    emoji = "🍂"
    duration_range = [1,2]

    leaves = ["orange", "brown", "yellow", "red", "fake", "real", "green", "magenta", "violet", "black", "infrared", "cosmic", "microscopic", "celestial", "spiritual", "ghostly", "transparent"]
    eddy_types = [" cloud", " small tornado", "n orb", " sheet", "n eddy", " smattering", " large number", " pair"]
    out_counter = 0
    sent = False
    first = True
    

    def __init__(self, game):
        self.name = f"Leaf Eddies: {roman.roman_convert(str(game.max_innings*3))}"
        self.original_innings = game.max_innings
        game.max_innings = 1
        self.inning_text = "The umpires have remembered their jobs. They shoo the defenders off the field!"

    def activate(self, game, result):
        if game.inning == 1:
            if self.out_counter % 3 == 0 and not self.out_counter == 0 and not self.sent:
                if self.first:
                    self.first = False
                    updatetext = "The leaves have distracted the umpires, and they've been unable to keep track of outs!"               
                else:
                    leaf = random.sample(self.leaves, 2)
                    eddy = random.choice(self.eddy_types)
                    updatetext = f"A{eddy} of {leaf[0]} and {leaf[1]} leaves blows through, and the umpires remain distracted!"
                self.sent = True
                result.clear()
                result.update({
                        "text": updatetext,
                        "text_only": True,
                        "weather_message": True
                    })
        else:
            game.outs = 2

    def steal_post_activate(self, game, result):
        self.post_activate(game, result)

    def post_activate(self, game, result):
        if game.inning == 1:
            if game.outs > 0:
                self.out_counter += game.outs
                game.outs = 0
                self.sent = False
                if self.out_counter < (self.original_innings * 3):
                    self.name = f"Leaf Eddies: {roman.roman_convert(str(self.original_innings*3-self.out_counter))}"
                else:
                    self.name = "Leaf Eddies"
                    self.out_counter = 0
                    game.outs = 3
        elif game.teams["home"].score != game.teams["away"].score:
            game.outs = 3
            if game.top_of_inning:
                game.inning += 1
                game.top_of_inning = False

    def modify_top_of_inning_message(self, game, state):
        state["update_emoji"] = self.emoji
        if game.inning == 1:
            self.name = f"Leaf Eddies: {roman.roman_convert(str(self.original_innings*3-self.out_counter))}"
        else:
            self.name = "Leaf Eddies: Golden Run"
            state["update_emoji"] = "⚠"
            self.inning_text = "SUDDEN DEATH ⚠"
        state["update_text"] = self.inning_text
        state["weather_text"] = self.name

    def modify_atbat_message(self, game, state):
        if game.inning == 1:
            state["weather_text"] = self.name

class Smog(Weather):
    name = "Smog"
    emoji = "🚌"
    duration_range = [1,2]

    def __init__(self, game):
        game.random_weather_flag = True
        setattr(game, "weather", random.choice(list(safe_weathers().values()))(game))

class Dusk(Weather):
    name = "Dusk"
    emoji = "🌆"
    duration_range = [2,3]

    def __init__(self, game):
        for team in game.teams.values():
            random.shuffle(team.lineup)

    def activate(self, game, result):
        if result["outcome"] in [appearance_outcomes.strikeoutlooking, appearance_outcomes.strikeoutswinging, appearance_outcomes.groundout, appearance_outcomes.flyout, appearance_outcomes.fielderschoice, appearance_outcomes.doubleplay, appearance_outcomes.sacrifice]:
            result["offense_team"].lineup_position -= 1
            result["weather_message"] = True
            if game.outs >= 2 or (game.outs >= 1 and result["outcome"] == appearance_outcomes.doubleplay):
                result["displaytext"] += random.choice([" A shade returns to the dugout with them, waiting.",
                                                        " They return to the dugout alongside a shade.",
                                                        " A shade waits patiently."])
            else:
                if random.random() < 0.01:
                    result["displaytext"] += " But it refused."
                else:
                    result["displaytext"] += random.choice([" They leave a shade behind!",
                                                            " A shade of the self remains.",
                                                            " They leave a shade in the light of the setting sun.",
                                                            " They return to the dugout, but their shade remains.",
                                                            " They leave a shade at the plate for another plate appearance.",
                                                            " Their shade refuses to leave the plate, and shoulders the bat."])


def all_weathers():
    weathers_dic = {
            "Supernova" : Supernova,
            "Midnight": Midnight,
            "Slight Tailwind": SlightTailwind,
            "Blizzard": Blizzard,
            "Twilight" : Twilight, 
            "Thinned Veil" : ThinnedVeil,
            "Heat Wave" : HeatWave,
            "Drizzle" : Drizzle,
            "Breezy": Breezy,
            "Starlight" : Starlight,
            "Meteor Shower" : MeteorShower,
            "Hurricane" : Hurricane,
            "Tornado" : Tornado,
            "Torrential Downpour" : Downpour,
            "Summer Mist" : SummerMist,
            "Leaf Eddies" : LeafEddies,
            "Smog" : Smog,
            "Dusk" : Dusk
        }
    return weathers_dic

def safe_weathers():
    """weathers safe to swap in mid-game"""
    weathers_dic = {
            "Supernova" : Supernova,
            "Midnight": Midnight,
            "Slight Tailwind": SlightTailwind,
            "Twilight" : Twilight, 
            "Thinned Veil" : ThinnedVeil,
            "Drizzle" : Drizzle,
            "Breezy": Breezy,
            "Starlight" : Starlight,
            "Meteor Shower" : MeteorShower,
            "Hurricane" : Hurricane,
            "Tornado" : Tornado,
            "Summer Mist" : SummerMist,
            "Dusk" : Dusk
        }
    return weathers_dic

class WeatherChains():
    light = [SlightTailwind, Twilight, Breezy, Drizzle, SummerMist, LeafEddies] #basic starting points for weather, good comfortable spots to return to
    magic = [Twilight, ThinnedVeil, MeteorShower, Starlight, Dusk] #weathers involving breaking the fabric of spacetime
    sudden = [Tornado, Hurricane, Twilight, Starlight, Midnight, Downpour, Smog] #weathers that always happen and leave over 1-3 games
    disaster = [Hurricane, Tornado, Downpour, Blizzard] #storms
    aftermath = [Midnight, Starlight, MeteorShower, SummerMist, Dusk] #calm epilogues

    dictionary = {
            #Supernova : (magic + sudden + disaster, None), supernova happens leaguewide and shouldn't need a chain, but here just in case
            Midnight : ([SlightTailwind, Breezy, Drizzle, Starlight, MeteorShower, HeatWave, SummerMist],[2,2,2,4,4,1,2]),
            SlightTailwind : ([Breezy, Drizzle, LeafEddies, Smog, Tornado], [3,3,3,3,1]),
            Blizzard : ([Midnight, Starlight, MeteorShower, Twilight, Downpour, Dusk], [2,2,2,2,4,2]),
            Twilight : ([ThinnedVeil, Midnight, MeteorShower, SlightTailwind, SummerMist], [2,4,2,1,2]),
            ThinnedVeil : (light, None),
            HeatWave : ([Tornado, Hurricane, SlightTailwind, Breezy, SummerMist, Dusk],[4,4,1,1,2,1]),
            Drizzle : ([Hurricane, Downpour, Blizzard],[2,2,1]),
            Breezy : ([Drizzle, HeatWave, Blizzard, Smog, Tornado], [3,3,1,3,1]),
            Starlight : ([SlightTailwind, Twilight, Breezy, Drizzle, ThinnedVeil, HeatWave], None),
            MeteorShower : ([Starlight, ThinnedVeil, HeatWave, Smog], None),
            Hurricane : ([LeafEddies, Midnight, Starlight, MeteorShower, Twilight, Downpour], [3,2,2,2,2,4]),
            Tornado : ([LeafEddies, Midnight, Starlight, MeteorShower, Twilight, Downpour],[3,2,2,2,2,4]),
            SummerMist : ([Drizzle, Breezy, Hurricane, Downpour, Dusk],[2, 1, 1, 1,4]),
            LeafEddies : ([Breezy, Tornado, SummerMist, ThinnedVeil, Smog], None),
            Downpour : (aftermath, None),
            Smog : (disaster + [Drizzle], None),
            Dusk : ([ThinnedVeil, Midnight, MeteorShower, Starlight], [4,2,2,3])
        }

    chains = [
            [Hurricane, Drizzle, Hurricane]
        ]

    def chain_weather(weather_instance):
        #weather_type = type(weather_instance)
        weather_type = weather_instance
        options, weight = WeatherChains.dictionary[weather_type]
        return random.choices(options, weights = weight)[0]

    def parent_weathers(weather_type):
        parents = []
        for this_weather, (children, _) in WeatherChains.dictionary.items():
            if weather_type in children:
                parents.append(this_weather)
        return parents

    def starting_weather():
        return random.choice(WeatherChains.light + WeatherChains.magic)

    def debug_weathers():
        names = ["a.txt", "b.txt", "c.txt"]
        for name in names:
            current = random.choice(list(all_weathers().values()))
            out = ""
            for i in range(0,50):
                out += f"{current.name} {current.emoji}\n"
                current = WeatherChains.chain_weather(current)
            
            with open("data/"+name, "w", encoding='utf-8') as file:
                file.write(out)
