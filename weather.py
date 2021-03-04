import random, math, roman
from gametext import appearance_outcomes, base_string

class Weather:
    def __init__(self, game):
        self.name = "Sunny"
        self.emoji = "🌞"

    def __str__(self):
        return f"{self.emoji} {self.name}"

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


class Supernova(Weather):
    def __init__(self, game):
        self.name = "Supernova"
        self.emoji = "🌟"
        self.duration = random.randint(1,2)

    def modify_atbat_stats(self, roll):
        roll["pitch_stat"] *= 0.8

class Midnight(Weather):
    def __init__(self, game):
        self.name = "Midnight"
        self.emoji = "🕶"
        self.duration = 1

    def modify_steal_stats(self, roll):
        roll["run_stars"] *= 2

class SlightTailwind(Weather):
    def __init__(self, game):
        self.name = "Slight Tailwind"
        self.emoji = "🏌️‍♀️"
        self.duration = random.randint(2,4)

    def activate(self, game, result):

        if "mulligan" not in game.last_update[0].keys() and not result["ishit"] and result["text"] != appearance_outcomes.walk: 
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
    def __init__(self, game):
        self.name = "Starlight"
        self.emoji = "🌃"
        self.duration = 2

    def activate(self, game, result):

        if (result["text"] == appearance_outcomes.homerun or result["text"] == appearance_outcomes.grandslam):
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
    def __init__(self, game):
        self.name = "Blizzard"
        self.emoji = "❄"
        self.duration = random.randint(3,6)

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
    def __init__(self,game):
        self.name = "Twilight"
        self.emoji = "👻"
        self.duration = random.randint(2,3)

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
    def __init__(self,game):
        self.name = "Thinned Veil"
        self.emoji = "🌌"
        self.duration = random.randint(2,4)

    def activate(self, game, result):
        if result["ishit"]:
           if result["text"] == appearance_outcomes.homerun or result["text"] == appearance_outcomes.grandslam:
                result["veil"] = True

    def modify_atbat_message(self, game, state):
        if "veil" in game.last_update[0].keys():
            state["update_emoji"] = self.emoji    
            state["update_text"] += f" {game.last_update[0]['batter']}'s will manifests on {base_string(game.last_update[1])} base."

class HeatWave(Weather):
    def __init__(self,game):
        self.name = "Heat Wave"
        self.emoji = "🌄"
        self.duration = random.randint(3,6)

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
    def __init__(self,game):
        self.name = "Drizzle"
        self.emoji = "🌧"
        self.duration = random.randint(2,3)

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
    def __init__(self, game):
        self.name = "Breezy"
        self.emoji = "🎐"
        self.duration = random.randint(1,4)
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
                first_first_letter = names[0][0]
                last_first_letter = names[-1][0]
                names[0] = last_first_letter + names[0][1:]
                names[-1] = first_first_letter + names[-1][1:]
                player.name = ' '.join(names)
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
    def __init__(self, game):
        self.name = "Meteor Shower"
        self.emoji = "🌠"
        self.duration = random.randint(3,6)
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
    def __init__(self, game):
        self.name = "Hurricane"
        self.emoji = "🌀"
        self.duration = 1

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
    def __init__(self, game):
        self.name = "Tornado"
        self.emoji = "🌪"
        self.duration = random.randint(1,2)

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
    def __init__(self, game):
        self.target = game.max_innings
        self.name = f"Torrential Downpour: {roman.roman_convert(str(self.target))}"
        self.emoji = '⛈'
        self.duration = random.randint(2,5)
        

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
        state["update_text"] = "The gods are not yet pleased. Play continues through the storm."

    def modify_game_end_message(self, game, state):
        state["update_emoji"] = self.emoji
        state["update_text"] = f"{self.target} runs are reached, pleasing the gods. The storm clears."
            

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
            "Torrential Downpour" : Downpour
        }
    return weathers_dic

class WeatherChains():
    light = [SlightTailwind, Twilight, Breezy, Drizzle] #basic starting points for weather, good comfortable spots to return to
    magic = [Twilight, ThinnedVeil, MeteorShower, Starlight] #weathers involving breaking the fabric of spacetime
    sudden = [Tornado, Hurricane, Twilight, Starlight, Midnight, Supernova] #weathers that always happen and leave over 1-3 games
    disaster = [Hurricane, Tornado, Downpour, Blizzard] #storms
    aftermath = [Midnight, Starlight, MeteorShower] #calm epilogues