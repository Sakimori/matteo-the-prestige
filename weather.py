import random
import math
from gametext import appearance_outcomes

class Weather:
    def __init__(self, game):
        self.name = "Sunny"
        self.emoji = "🌞" + "\uFE00"

    def __str__(self):
        return f"{self.emoji} {self.name}"

    def activate(self, game, result):
        # activates after the batter calculation. modify result, or just return another thing
        pass

    def on_flip_inning(self, game):
        pass

    def on_choose_next_batter(self, game):
        pass

    def modify_steal_stats(self, roll):
        pass

    def modify_atbat_stats(self, player_rolls):
        # Activates before batting
        pass

    def modify_atbat_roll(self, outcome, roll, defender):
        pass

class Supernova(Weather): # todo
    def __init__(self, game):
        self.name = "Supernova"
        self.emoji = "🌟" + "\uFE00"

    def modify_atbat_stats(self, roll):
        roll["pitch_stat"] *= 0.9

class Midnight(Weather): # todo
    def __init__(self, game):
        self.name = "Midnight"
        self.emoji = "🕶" + "\uFE00"

    def modify_steal_stats(self, roll):
        roll["run_stars"] *= 2

class SlightTailwind(Weather):
    def __init__(self, game):
        self.name = "Slight Tailwind"
        self.emoji = "🏌️‍♀️" + "\uFE00"

    def activate(self, game, result):
        if game.top_of_inning:
            offense_team = game.teams["away"]
            weather_count = self.counter_away
            defense_team = game.teams["home"]
        else:
            offense_team = game.teams["home"]
            weather_count = self.counter_home
            defense_team = game.teams["away"]

        if "mulligan" not in game.last_update[0].keys() and not result["ishit"] and result["text"] != appearance_outcomes.walk: 
            mulligan_roll_target = -((((self.get_batter().stlats["batting_stars"])-5)/6)**2)+1
            if random.random() > mulligan_roll_target and self.get_batter().stlats["batting_stars"] <= 5:
                result["mulligan"] = True
                result["weather_message"] = True

class HeavySnow(Weather):
    def __init__(self, game):
        self.name = "Heavy Snow"
        self.emoji = "❄" + "\uFE00"
        self.counter_away = random.randint(0,len(game.teams['away'].lineup)-1)
        self.counter_home = random.randint(0,len(game.teams['home'].lineup)-1)

    def activate(self, game, result):        
        if game.top_of_inning:
            offense_team = game.teams["away"]
            weather_count = self.counter_away
        else:
            offense_team = game.teams["home"]
            weather_count = self.counter_home

        if weather_count == offense_team.lineup_position and "snow_atbat" not in game.last_update[0].keys():
            result.clear()
            result.update({
                "snow_atbat": True,
                "text": f"{offense_team.lineup[offense_team.lineup_position % len(offense_team.lineup)].name}'s hands are too cold! {game.get_batter().name} is forced to bat!",
                "text_only": True,
                "weather_message": True,
            })

    def on_flip_inning(self, game):
        if game.top_of_inning and self.counter_away < game.teams["away"].lineup_position:
            self.counter_away = game.pitcher_insert(game.teams["away"])

        if not game.top_of_inning and self.counter_home < game.teams["home"].lineup_position:
            self.counter_home = game.pitcher_insert(game.teams["home"])

    def on_choose_next_batter(self, game):
        if game.top_of_inning:
            bat_team = game.teams["away"]
            counter = self.counter_away
        else:
            bat_team = game.teams["home"]
            counter = self.counter_home

        if counter == bat_team.lineup_position:
            game.current_batter = bat_team.pitcher

class Twilight(Weather):
    def __init__(self,game):
        self.name = "Twilight"
        self.emoji = "👻" + "\uFE00"

    def modify_atbat_roll(self, outcome, roll, defender):
        error_line = - (math.log(defender.stlats["defense_stars"] + 1)/50) + 1
        error_roll = random.random()
        if error_roll > error_line:
            outcome["error"] = True
            outcome["weather_message"] = True
            outcome["defender"] = defender
            roll["pb_system_stat"] = 0.1

class ThinnedVeil(Weather):
    def __init__(self,game):
        self.name = "Thinned Veil"
        self.emoji = "🌌" + "\uFE00"

    def activate(self, game, result):
        if result["ishit"]:
           if result["text"] == appearance_outcomes.homerun or result["text"] == appearance_outcomes.grandslam:
                result["veil"] = True
                result["weather_message"] = True

class HeatWave(Weather):
    def __init__(self,game):
        self.name = "Heat Wave"
        self.emoji = "🌄" + "\uFE00"

        self.counter_away = -1 # random.randint(2,4)
        self.counter_home = -1 # random.randint(2,4)

    def on_flip_inning(self, game):
        current_pitcher = game.get_pitcher()
        if game.top_of_inning:
            bat_team = game.teams["home"]
            counter = self.counter_home
        else:
            bat_team = game.teams["away"]
            counter = self.counter_away

        should_change_pitcher = False
        if game.inning >= counter:
            should_change_pitcher = True
            if game.top_of_inning:
                self.counter_home = self.counter_home - (self.counter_home % 5) + 5 + random.randint(1,4) #rounds down to last 5, adds up to next 5. then adds a random number 2<=x<=5 to determine next pitcher                       
            else:
                self.counter_away = self.counter_away - (self.counter_away % 5) + 5 + random.randint(1,4)      

        if should_change_pitcher:
            tries = 0
            while game.get_pitcher() == current_pitcher and tries < 3:
                bat_team.set_pitcher(use_lineup = True)
                tries += 1

class Drizzle(Weather):
    def __init__(self,game):
        self.name = "Drizzle"
        self.emoji = "🌧"

    def on_flip_inning(self, game):
        if game.top_of_inning:
            next_team = "away"
        else:
            next_team = "home"

        lineup = game.teams[next_team].lineup
        game.bases[2] = lineup[(game.teams[next_team].lineup_position-1) % len(lineup)]

class Sun2(Weather):
    def __init__(self, game):
        self.name = "Sun 2"


    def activate(self, game):
        for teamtype in game.teams:
            team = game.teams[teamtype]
            if team.score >= 10:
                team.score -= 10
            # no win counting yet :(
            result.clear()
            result.update({
                "text": "The {} collect 10! Sun 2 smiles.".format(team.name),
                "text_only": True,
            })

class NameSwappyWeather(Weather):
    def __init__(self, game):
        self.name = "Literacy"
        self.emoji = "📚"
        self.activation_chance = 0.01

    def activate(self, game, result):
        if random.random() < self.activation_chance:
            teamtype = random.choice(["away","home"])
            team = game.teams[teamtype]
            player = random.choice(team.lineup)
            old_player_name = player.name
            if ' ' in player.name:
                names = player.name.split(" ")
                first_first_letter = names[0][0]
                last_first_letter = names[-1][0]
                names[0] = last_first_letter + names[0][1:]
                names[-1] = first_first_letter + names[-1][1:]
                player.name = ' '.join(names)
            else:
                #name is one word, so turn 'bartholemew' into 'martholebew'
                first_letter = player.name[0]
                last_letter = player.name[-1]
                player.name = last_letter + player.name[1:-1] + last_letter

            book_adjectives = ["action-packed", "historical", "friendly", "rude", "mystery", "thriller", "horror", "sci-fi", "fantasy", "spooky","romantic"]
            book_types = ["novel","novella","poem","anthology","fan fiction","tablet","carving", "autobiography"]
            book = "{} {}".format(random.choice(book_adjectives),random.choice(book_types))

            result.clear()
            result.update({
                "text": "{} stopped to read a {} and became Literate! {} is now {}!".format(old_player_name, book, old_player_name, player.name),
                "text_only": True,
                "weather_message": True
            })


class Feedback(Weather):
    def __init__(self, game):
        self.name = "Feedback"
        self.emoji = "🎤"
        self.activation_chance = 0.02
        self.swap_batter_vs_pitcher_chance = 0.8

    def activate(self, game, result):
        if random.random() < self.activation_chance:
            # feedback time
            player1 = None
            player2 = None
            team1 = game.teams["home"]
            team2 = game.teams["away"]
            if random.random() < self.swap_batter_vs_pitcher_chance:
                # swapping batters
                # theoretically this could swap players already on base :(
                team1 = game.teams["home"]
                team2 = game.teams["away"]
                homePlayerIndex = random.randint(0,len(team1.lineup)-1)
                awayPlayerIndex = random.randint(0,len(team2.lineup)-1)

                player1 = team1.lineup[homePlayerIndex]
                player2 = team2.lineup[awayPlayerIndex]

                team1.lineup[homePlayerIndex] = player2
                team2.lineup[awayPlayerIndex] = player1
            else:
                # swapping pitchers
                player1 = team1.pitcher
                player2 = team2.pitcher

                team1.pitcher = player2
                team2.pitcher = player1

            result.clear()
            result.update({
                "text": "{} and {} switched teams in the feedback!".format(player1.name,player2.name),
                "text_only": True,
                "weather_message": True,
            })

def all_weathers():
    weathers_dic = {
        #"Supernova" : Supernova,
        #"Midnight": Midnight,
        #"Slight Tailwind": SlightTailwind,
       "Heavy Snow": HeavySnow, # works
        "Twilight" : Twilight, # works
       "Thinned Veil" : ThinnedVeil, # works
        "Heat Wave" : HeatWave,
        "Drizzle" : Drizzle, # works
#        "Sun 2": Sun2,
        "Feedback": Feedback,
        "Literacy": NameSwappyWeather,
        }
    return weathers_dic

