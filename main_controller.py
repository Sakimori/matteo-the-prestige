import asyncio, time, datetime, games, json, threading, jinja2, leagues, os, leagues, gametext
from leagues import league_structure
from league_storage import league_exists
from flask import Flask, url_for, Response, render_template, request, jsonify, send_from_directory, abort
from flask_socketio import SocketIO, emit
import database as db

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

### API

@app.route('/api/teams/search')
def search_teams():
    query = request.args.get('query')
    page_len = int(request.args.get('page_len'))
    page_num = int(request.args.get('page_num'))

    if query is None:
        abort(400, "A query term is required")

    result = db.search_teams(query)
    if page_len is not None: #pagination should probably be done in the sqlite query but this will do for now
        if page_num is None:
            abort(400, "A page_len argument must be accompanied by a page_num argument")
        result = result[page_num*page_len : (page_num + 1)*page_len]

    return jsonify([json.loads(x[0])['name'] for x in result]) #currently all we need is the name but that can change

MAX_SUBLEAGUE_DIVISION_TOTAL = 22;
MAX_TEAMS_PER_DIVISION = 12;

@app.route('/api/leagues', methods=['POST'])
def create_league():
    config = json.loads(request.data)

    if league_exists(config['name']):
        return jsonify({'status':'err_league_exists'}), 400

    num_subleagues = len(config['structure']['subleagues'])
    if num_subleagues < 1 or num_subleagues % 2 != 0:
        return jsonify({'status':'err_invalid_subleague_count'}), 400

    num_divisions = len(config['structure']['subleagues'][0]['divisions'])
    if num_subleagues * (num_divisions + 1) > MAX_SUBLEAGUE_DIVISION_TOTAL:
        return jsonify({'status':'err_invalid_subleague_division_total'}), 400

    league_dic = {}
    all_teams = set()
    err_teams = []
    for subleague in config['structure']['subleagues']:
        if subleague['name'] in league_dic:
            return jsonify({'status':'err_duplicate_name', 'cause':subleague['name']})

        subleague_dic = {}
        for division in subleague['divisions']:
            if division['name'] in subleague_dic:
                return jsonify({'status':'err_duplicate_name', 'cause':f"{subleague['name']}/{division['name']}"}), 400
            elif len(division['teams']) > MAX_TEAMS_PER_DIVISION:
                return jsonify({'status':'err_too_many_teams', 'cause':f"{subleague['name']}/{division['name']}"}), 400

            teams = []
            for team_name in division['teams']:
                if team_name in all_teams:
                    return jsonify({'status':'err_duplicate_team', 'cause':team_name}), 400
                all_teams.add(team_name)
                
                team = games.get_team(team_name)
                if team is None:
                    err_teams.append(team_name)
                else:
                    teams.append(team)
            subleague_dic[division['name']] = teams
        league_dic[subleague['name']] = subleague_dic

    if len(err_teams) > 0:
        return jsonify({'status':'err_no_such_team', 'cause': err_teams}), 400

    for (key, min_val) in [
        ('division_series', 1), 
        ('inter_division_series', 1), 
        ('inter_league_series', 1)
    ]:
        if config[key] < min_val:
            return jsonify({'status':'err_invalid_optiion_value', 'cause':key}), 400

    new_league = league_structure(config['name'])
    new_league.setup(
        league_dic, 
        division_games=config['division_series'],
        inter_division_games=config['inter_division_series'],
        inter_league_games=config['inter_league_series'],
    )
    new_league.constraints["division_leaders"] = config["top_postseason"]
    new_league.constraints["wild_cards"] = config["wildcards"]
    new_league.generate_schedule()
    leagues.save_league(new_league)

    return jsonify({'status':'success_league_created'})



### SOCKETS

thread2 = threading.Thread(target=socketio.run,args=(app,'0.0.0.0'))
thread2.start()

master_games_dic = {} #key timestamp : (game game, {} state)
game_states = []

@socketio.on("recieved")
def handle_new_conn(data):
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
            if not this_game.play_has_begun:                    #weather_emoji
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

                if state["update_pause"] == 1: #generate the top of the inning message before displaying the at bat result
                    state["update_emoji"] = "🍿"
                    if this_game.over: # game over message
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
                    else:
                        if this_game.top_of_inning: 
                            state["update_text"] = f"Top of {this_game.inning}. {this_game.teams['away'].name} batting!"
                        else:
                            if this_game.inning >= this_game.max_innings:
                                if this_game.teams["home"].score > this_game.teams["away"].score:
                                    this_game.victory_lap = True
                            state["update_text"] = f"Bottom of {this_game.inning}. {this_game.teams['home'].name} batting!"

                        this_game.weather.modify_top_of_inning_message(this_game, state)


                elif state["update_pause"] != 1 and this_game.play_has_begun:

                    if "weather_message" in this_game.last_update[0].keys():
                        state["update_emoji"] = this_game.weather.emoji
                    elif "ishit" in this_game.last_update[0] and this_game.last_update[0]["ishit"]:
                        state["update_emoji"] = "🏏"
                    elif this_game.last_update[0]["text"] == gametext.appearance_outcomes.walk:
                        state["update_emoji"] = "👟"
                    else:
                        state["update_emoji"] = "🗞"

                    if "steals" in this_game.last_update[0].keys():
                        updatestring = ""
                        for attempt in this_game.last_update[0]["steals"]:
                            updatestring += attempt + "\n"

                        state["update_emoji"] = "💎" 
                        state["update_text"] = updatestring

                    elif "text_only" in this_game.last_update[0].keys(): #this handles many weather messages
                        state["update_text"] = this_game.last_update[0]["text"]
                    else:
                        updatestring = ""
                        punc = ""
                        if this_game.last_update[0]["defender"] != "":
                            punc = ". "

                        if "fc_out" in this_game.last_update[0].keys():
                            name, out_at_base_string = this_game.last_update[0]['fc_out']
                            updatestring = f"{this_game.last_update[0]['batter']} {this_game.last_update[0]['text'].value.format(name, out_at_base_string)} {this_game.last_update[0]['defender']}{punc}"
                        else:
                            updatestring = f"{this_game.last_update[0]['batter']} {this_game.last_update[0]['text'].value} {this_game.last_update[0]['defender']}{punc}"
                        if this_game.last_update[1] > 0:
                                updatestring += f"{this_game.last_update[1]} runs scored!"


                        state["update_text"] = updatestring

                        this_game.weather.modify_atbat_message(this_game, state)

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