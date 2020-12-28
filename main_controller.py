import asyncio, time, datetime, games, json, threading
from flask import Flask, url_for, Response

app = Flask("the-prestige")

@app.route('/')
def hello():
    return url_for("boop")

@app.route("/gotoboop")
def boop():
    return states_to_send

thread2 = threading.Thread(target=app.run)
thread2.start()

master_games_dic = {} #key timestamp : (game game, {} state)
states_to_send = {}

def update_loop():
    while True:
        game_times = iter(master_games_dic.copy().keys())
        for game_time in game_times:
            this_game, state = master_games_dic[game_time]
            test_string = this_game.gamestate_display_full()
            
            state["display_inning"] = this_game.inning          #games need to be initialized with the following keys in state:
            state["outs"] = this_game.outs                      #away_name
            state["pitcher"] = this_game.get_pitcher().name     #home_name
            state["batter"] = this_game.get_batter().name       #max_innings
            state["away_score"] = this_game.teams["away"].score #top_of_inning = True
            state["home_score"] = this_game.teams["home"].score #update_pause = 0
                                                                #victory_lap = False
            if test_string == "Game not started.":              #weather_emoji
                state["update_emoji"] = "🍿"                    #weather_text
                state["update_text"] = "Play blall!"            #they also need a timestamp
                state["delay"] -= 1
            
            if state["delay"] <= 0:
                if this_game.top_of_inning != state["top_of_inning"]:
                    state["update_pause"] = 2
                    state["pitcher"] = "-"
                    state["batter"] = "-"
                    if state["top_of_inning"]:
                        state["display_inning"] -= 1

                if state["update_pause"] == 1:
                    state["update_emoji"] = "🍿"
                    if this_game.top_of_inning:
                        state["update_text"] = f"Top of {this_game.inning}. {this_game.teams['away'].name} batting!"
                    else:
                        if this_game.inning >= this_game.max_innings:
                            if this_game.teams["home"].score > this_game.teams["away"].score:
                                state["victory_lap"] = True
                        state["update_text"] = f"Bottom of {this_game.inning}. {this_game.teams['home'].name} batting!"

                elif state["update_pause"] != 1 and test_string != "Game not started.":
                    if "steals" in this_game.last_update[0].keys():
                        updatestring = ""
                        for attempt in this_game.last_update[0]["steals"]:
                            updatestring += attempt + "\n"

                        state["emoji"] = "💎" 
                        state["update_text"] = updatestring

                    else:
                        updatestring = ""
                        punc = ""
                        if this_game.last_update[0]["defender"] != "":
                            punc = ". "

                        if "fc_out" in this_game.last_update[0].keys():
                            name, base_string = this_game.last_update[0]['fc_out']
                            updatestring = f"{this_game.last_update[0]['batter']} {this_game.last_update[0]['text'].value.format(name, base_string)} {this_game.last_update[0]['defender']}{punc}"
                        else:
                            updatestring = f"{this_game.last_update[0]['batter']} {this_game.last_update[0]['text'].value} {this_game.last_update[0]['defender']}{punc}"
                        if this_game.last_update[1] > 0:
                                updatestring += f"{this_game.last_update[1]} runs scored!"

                        state["emoji"] = "🏏"
                        state["update_text"] = updatestring

            state["bases"] = this_game.named_bases()

            state["top_of_inning"] = this_game.top_of_inning

            states_to_send[game_time] = state

            if state["update_pause"] <= 1 and state["delay"] < 0:
                this_game.gamestate_update_full()

            state["update_pause"] -= 1

        time.sleep(6)