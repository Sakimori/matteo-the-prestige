import random
class Weather:
    def __init__(self):
        self.name = "None"
    def activate(self, game, result):
        pass

class Sun2(Weather):
    def __init__(self):
        self.name = "Sun 2"
    def activate(self, game):
        for teamtype in game.teams:
            team = game.teams[teamtype]
            if team.score >= 10:
                team.score -= 10
            # no win counting yet :(
            result = {
             "text": "The {} collect 10! Sun 2 smiles.".format(team.name)
            }
            return result
        return None

class NameSwappyWeather(Weather):
    def __init__(self):
        self.name = "Literacy"
        self.activation_chance = 0.01
    def activate(self, game):
        if random.random() < self.activation_chance:
            teamtype = random.choice(["away","home"])
            team = game.teams[teamtype]
            player = random.choice(team.lineup)
            old_player_name = player.name
            if ' ' in player.name:
                names = player.name.split(" ")
                first_first_letter = names[0][0]
                last_first_letter = names[-1][0]
                names[0][0] = last_first_letter
                names[-1][0] = first_first_letter
                player.name = ' '.join(names)
            else:
                #name is one word, so turn 'bartholemew' into 'martholebew'
                first_letter = player.name[0]
                last_letter = player.name[-1]
                player.name[0] = last_letter
                player.name[-1] = first_letter

            result = {
             "text": "{} is Literate! {} is now {}!".format(old_player_name,old_player_name, player.name)
            }
            return result
        return None

class Feedback(Weather):
    def __init__(self):
        self.name = "Feedback"
        self.activation_chance = 0.01
        self.swap_batter_vs_pitcher_chance = 0.8
    def activate(self, game):
        if random.random() < self.activation_chance:
            # feedback time
            result = {}
            player1 = None
            player2 = None
            if random.random() < self.swap_batter_vs_pitcher_chance:
                # swapping batters
                # theoretically this could swap players already on base :(
                homePlayerIndex = random.randint(len(teams["home"].lineup))
                awayPlayerIndex = random.randint(len(teams["away"].lineup))

                homePlayer = teams["home"].lineup[homePlayerIndex]
                awayPlayer = teams["away"].lineup[awayPlayerIndex]

                teams["home"].lineup[homePlayerIndex] = awayPlayer
                teams["away"].lineup[awayPlayerIndex] = homePlayer
            else:
                # swapping pitchers
                player1 = teams["home"].pitcher
                player2 = teams["away"].pitcher
                teams["home"].set_pitcher(player2)
                teams["away"].set_pitcher(player1)
          
            result = {
                "text": "{} and {} switched teams in the feedback!".format(player1.name,player2.name),
            }
            return result
        return None


all_weathers = [
    Sun2,
    Feedback,
#    NameSwappyWeather,
    ]
