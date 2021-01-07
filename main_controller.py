import asyncio, time, datetime, games, json, threading, jinja2, leagues, os
from flask import Flask, url_for, Response, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

app = Flask("the-prestige", static_folder='simmadome/build')
app.config['SECRET KEY'] = 'dev'
#app.config['SERVER_NAME'] = '0.0.0.0:5000'
socketio = SocketIO(app)

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


thread2 = threading.Thread(target=socketio.run,args=(app,'0.0.0.0'))
thread2.start()

master_games_dic = {} #key timestamp : (game game, {} state)
game_states = []

@socketio.on("recieved")
def handle_new_conn(data):
    print("new connection")
    socketio.emit("states_update", game_states, room=request.sid)

def update_loop():
    global game_states
    while True:
        game_states = []
        game_ids = iter(master_games_dic.copy().keys())
        for game_id in game_ids:
            this_game, state, discrim_string = master_games_dic[game_id]
            test_string = this_game.gamestate_display_full()
            state["leagueoruser"] = discrim_string
            state["display_inning"] = this_game.inning          #games need to be initialized with the following keys in state:
                                                                #is_league, bool
            state["outs"] = this_game.outs                      #away_name
            state["pitcher"] = this_game.get_pitcher().name     #home_name
            state["batter"] = this_game.get_batter().name       #max_innings
            state["away_score"] = this_game.teams["away"].score #top_of_inning = True
            state["home_score"] = this_game.teams["home"].score #update_pause = 0
                                                                #victory_lap = False
            if test_string == "Game not started.":              #weather_emoji
                state["update_emoji"] = "🍿"                    #weather_text
                state["update_text"] = "Play blall!"            #they also need a timestamp
                state["start_delay"] -= 1
            
            state["display_top_of_inning"] = state["top_of_inning"]

            if state["start_delay"] <= 0:
                if this_game.top_of_inning != state["top_of_inning"]:
                    state["update_pause"] = 2
                    state["pitcher"] = "-"
                    state["batter"] = "-"
                    if not state["top_of_inning"]:
                        state["display_inning"] -= 1
                        state["display_top_of_inning"] = False

                if state["update_pause"] == 1:
                    state["update_emoji"] = "🍿"
                    if this_game.over:
                        state["display_inning"] -= 1
                        state["display_top_of_inning"] = False
                        winning_team = this_game.teams['home'].name if this_game.teams['home'].score > this_game.teams['away'].score else this_game.teams['away'].name
                        if this_game.victory_lap and winning_team == this_game.teams['home'].name:
                            state["update_text"] = f"{winning_team} wins with a victory lap!"
                        elif winning_team == this_game.teams['home'].name:
                            state["update_text"] = f"{winning_team} wins, shaming {this_game.teams['away'].name}!"
                        else:
                            state["update_text"] = f"{winning_team} wins!"
                        state["pitcher"] = "-"
                        state["batter"] = "-"
                    elif this_game.top_of_inning:
                        state["update_text"] = f"Top of {this_game.inning}. {this_game.teams['away'].name} batting!"
                    else:
                        if this_game.inning >= this_game.max_innings:
                            if this_game.teams["home"].score > this_game.teams["away"].score:
                                this_game.victory_lap = True
                        state["update_text"] = f"Bottom of {this_game.inning}. {this_game.teams['home'].name} batting!"

                elif state["update_pause"] != 1 and test_string != "Game not started.":
                    if "steals" in this_game.last_update[0].keys():
                        updatestring = ""
                        for attempt in this_game.last_update[0]["steals"]:
                            updatestring += attempt + "\n"

                        state["update_emoji"] = "💎" 
                        state["update_text"] = updatestring

                    elif "mulligan" in this_game.last_update[0].keys():
                        updatestring = ""
                        punc = ""
                        if this_game.last_update[0]["defender"] != "":
                            punc = ", "

                        state["update_emoji"] = "🏌️‍♀️"
                        state["update_text"] = f"{this_game.last_update[0]['batter']} would have gone out, but they took a mulligan!"

                    elif "snow_atbat" in this_game.last_update[0].keys():
                        state["update_emoji"] = "❄"
                        state["update_text"] = this_game.last_update[0]["text"]

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

                        state["update_emoji"] = "🏏"
                        state["update_text"] = updatestring

            state["bases"] = this_game.named_bases()

            state["top_of_inning"] = this_game.top_of_inning 

            game_states.append([game_id, state])

            if state["update_pause"] <= 1 and state["start_delay"] < 0:
                if this_game.over:
                    state["update_pause"] = 2
                    if state["end_delay"] < 0:
                        master_games_dic.pop(game_id)
                    else:
                        state["end_delay"] -= 1
                        master_games_dic[game_id][1]["end_delay"] -= 1
                else:
                    this_game.gamestate_update_full()

            state["update_pause"] -= 1

        socketio.emit("states_update", game_states)
        time.sleep(8)
