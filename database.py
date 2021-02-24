#handles the database interactions
import os, json, datetime, re
import sqlite3 as sql
from random import sample

data_dir = "data"

def create_connection():
    #create connection, create db if doesn't exist
    conn = None
    try:
        conn = sql.connect(os.path.join(data_dir, "matteo.db"))

        # enable write-ahead log for performance and resilience
        conn.execute('pragma journal_mode=wal')

        return conn
    except:
        print("oops, db connection no work")
        return conn


def initialcheck():
    conn = create_connection()
    soulscream_table_check_string = """ CREATE TABLE IF NOT EXISTS soulscreams (
                                            counter integer PRIMARY KEY,
                                            name text NOT NULL,
                                            soulscream text NOT NULL,
                                            timestamp text NOT NULL
                                        ); """

    player_cache_table_check_string = """ CREATE TABLE IF NOT EXISTS players (
                                            counter integer PRIMARY KEY,
                                            name text NOT NULL,
                                            json_string text NOT NULL,
                                            timestamp text NOT NULL
                                        ); """
    
    player_table_check_string = """ CREATE TABLE IF NOT EXISTS user_designated_players (
                                        user_id integer PRIMARY KEY,
                                        user_name text,
                                        player_id text NOT NULL,
                                        player_name text NOT NULL,
                                        player_json_string text NOT NULL
                                    );"""

    player_stats_table_check_string = """ CREATE TABLE IF NOT EXISTS stats (
                                            counter integer PRIMARY KEY,
                                            id text,
                                            name text,
                                            json_string text,
                                            outs_pitched integer DEFAULT 0,
                                            walks_allowed integer DEFAULT 0,
                                            hits_allowed integer DEFAULT 0,
                                            strikeouts_given integer DEFAULT 0,
                                            runs_allowed integer DEFAULT 0,
                                            plate_appearances integer DEFAULT 0,
                                            walks_taken integer DEFAULT 0,
                                            sacrifices integer DEFAULT 0,
                                            hits integer DEFAULT 0,
                                            home_runs integer DEFAULT 0,
                                            total_bases integer DEFAULT 0,
                                            rbis integer DEFAULT 0,
                                            strikeouts_taken integer DEFAULT 0
                                            );"""

    teams_table_check_string = """ CREATE TABLE IF NOT EXISTS teams (
                                            counter integer PRIMARY KEY,
                                            name text NOT NULL,
                                            team_json_string text NOT NULL,
                                            timestamp text NOT NULL,
                                            owner_id integer
                                        ); """

    one_big_league_check_string = """ CREATE TABLE IF NOT EXISTS one_big_league (
                                            counter integer PRIMARY KEY,
                                            team_name text NOT NULL,
                                            teams_beaten_list text,
                                            current_opponent_pool text,
                                            obl_points int DEFAULT 0,
                                            rival_name text
    );"""

    if conn is not None:
        c = conn.cursor()
        c.execute(soulscream_table_check_string)
        c.execute(player_cache_table_check_string)
        c.execute(player_table_check_string)
        c.execute(player_stats_table_check_string)
        c.execute(teams_table_check_string)
        c.execute(one_big_league_check_string)

    conn.commit()
    conn.close()

def get_stats(player_name):
    conn = create_connection()

    if conn is not None:
        c = conn.cursor()
        c.execute("SELECT * FROM players WHERE name=?", (player_name,))
        player = c.fetchone()
        try:
            cachetime = datetime.datetime.fromisoformat(player[3])
            if datetime.datetime.now(datetime.timezone.utc) - cachetime >= datetime.timedelta(days = 7):
                #delete old cache
                c.execute("DELETE FROM players WHERE name=?", (player_name,))
                conn.commit()
                conn.close()
                return None
        except TypeError:
            conn.close()
            return None

        conn.close()
        return player[2] #returns a json_string

    conn.close()
    return None

def cache_stats(name, json_string):
    conn = create_connection()
    store_string = """ INSERT INTO players(name, json_string, timestamp)
                            VALUES (?,?, ?) """

    if conn is not None:
        c = conn.cursor()
        c.execute(store_string, (name, json_string, datetime.datetime.now(datetime.timezone.utc)))
        conn.commit() 

    conn.close()


def get_soulscream(username):
    conn = create_connection()

    #returns none if not found or more than 3 days old
    if conn is not None:
        c = conn.cursor()
        c.execute("SELECT * FROM soulscreams WHERE name=?", (username,))
        scream = c.fetchone()
        
        try:
            cachetime = datetime.datetime.fromisoformat(scream[3])
            if datetime.datetime.now(datetime.timezone.utc) - cachetime >= datetime.timedelta(days = 7):
                #delete old cache
                c.execute("DELETE FROM soulscreams WHERE name=?", (username,))
                conn.commit()
                conn.close()
                return None
        except TypeError:
            conn.close()
            return None
        
        conn.close()
        return scream[2]

    conn.close()
    return None



def cache_soulscream(username, soulscream):
    conn = create_connection()
    store_string = """ INSERT INTO soulscreams(name, soulscream, timestamp)
                            VALUES (?,?, ?) """

    if conn is not None:
        c = conn.cursor()
        c.execute(store_string, (username, soulscream, datetime.datetime.now(datetime.timezone.utc)))
        conn.commit() 

    conn.close()


def designate_player(user, player_json):
    conn = create_connection()
    store_string = """ INSERT INTO user_designated_players(user_id, user_name, player_id, player_name, player_json_string)
                        VALUES (?, ?, ?, ?, ?)"""

    user_player = get_user_player_conn(conn, user)
    c = conn.cursor()
    if user_player is not None:
        c.execute("DELETE FROM user_designated_players WHERE user_id=?", (user.id,)) #delete player if already exists
    c.execute(store_string, (user.id, user.name, player_json["id"], player_json["name"], json.dumps(player_json)))
            
    conn.commit()
    conn.close()

def get_user_player_conn(conn, user): 
    try:
        if conn is not None:
            c = conn.cursor()
            c.execute("SELECT player_json_string FROM user_designated_players WHERE user_id=?", (user.id,))
            try:
                return json.loads(c.fetchone()[0])
            except TypeError:
                return False
        else:
            conn.close()
            return False
    except:
        conn.close()
        return False
    conn.close()
    return False

def get_user_player(user): 
    conn = create_connection()
    player = get_user_player_conn(conn, user)
    conn.close()
    return player

def save_team(name, team_json_string, user_id):
    conn = create_connection()
    try:
        if conn is not None:
            c = conn.cursor()
            store_string = """ INSERT INTO teams(name, team_json_string, timestamp, owner_id)
                            VALUES (?,?, ?, ?) """
            c.execute(store_string, (re.sub('[^A-Za-z0-9 ]+', '', name), team_json_string, datetime.datetime.now(datetime.timezone.utc), user_id)) #this regex removes all non-standard characters
            conn.commit() 
            conn.close()
            return True
        conn.close()
        return False
    except:
        return False
    conn.close()
    return False

def update_team(name, team_json_string):
    conn = create_connection()
    try:
        if conn is not None:
            c = conn.cursor()
            store_string = "UPDATE teams SET team_json_string = ? WHERE name=?"
            c.execute(store_string, (team_json_string, (re.sub('[^A-Za-z0-9 ]+', '', name)))) #this regex removes all non-standard characters
            conn.commit() 
            conn.close()
            return True
        conn.close()
        return False
    except:
        conn.close()
        return False
    conn.close()
    return False

def get_team(name, owner=False):
    conn = create_connection()
    if conn is not None:
        c = conn.cursor()
        if not owner:
            c.execute("SELECT team_json_string FROM teams WHERE name=?", (re.sub('[^A-Za-z0-9 ]+', '', name),)) #see above note re: regex
        else:
            c.execute("SELECT * FROM teams WHERE name=?", (re.sub('[^A-Za-z0-9 ]+', '', name),)) #see above note re: regex
        team = c.fetchone()
        
        conn.close()

        return team #returns a json string if owner is false, otherwise returns (counter, name, team_json_string, timestamp, owner_id)



    conn.close()
    return None

def delete_team(team):
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("DELETE FROM teams WHERE name=?", (re.sub('[^A-Za-z0-9 ]+', '', team.name),))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    conn.close()
    return False

def assign_owner(team_name, owner_id):
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("UPDATE teams SET owner_id = ? WHERE name = ?",(owner_id, re.sub('[^A-Za-z0-9 ]+', '', team_name)))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    conn.close()
    return False

def get_all_teams():
    conn = create_connection()
    if conn is not None:
        c = conn.cursor()
        c.execute("SELECT team_json_string FROM teams")
        team_strings = c.fetchall()
        conn.close()
        return team_strings

    conn.close()
    return None

def get_all_team_names():
    conn = create_connection()
    if conn is not None:
        c = conn.cursor()
        c.execute("SELECT name FROM teams")
        team_names = c.fetchall()
        team_names_out = [name for (name,) in team_names]
        conn.close()
        return team_names_out
    conn.close()
    return None

def get_filtered_teams(filter_list):
    teams_list = get_all_team_names()
    out_list = []
    for team in teams_list:
        if team not in filter_list:
            out_list.append(team)
    return out_list

def search_teams(search_string):
    conn = create_connection()
    if conn is not None:
        c = conn.cursor()
        c.execute("SELECT team_json_string FROM teams WHERE name LIKE ?",(re.sub('[^A-Za-z0-9 %]+', '', f"%{search_string}%"),))
        team_json_strings = c.fetchall()
        conn.close()
        return team_json_strings

    conn.close()
    return None

def add_stats(player_game_stats_list):
    conn = create_connection()
    if conn is not None:
        c=conn.cursor()
        for (name, player_stats_dic) in player_game_stats_list:
            c.execute("SELECT * FROM stats WHERE name=?",(name,))
            this_player = c.fetchone()
            if this_player is not None:
                for stat in player_stats_dic.keys():
                    c.execute(f"SELECT {stat} FROM stats WHERE name=?",(name,))
                    old_value = int(c.fetchone()[0])
                    c.execute(f"UPDATE stats SET {stat} = ? WHERE name=?",(player_stats_dic[stat]+old_value,name))
            else:
                c.execute("INSERT INTO stats(name) VALUES (?)",(name,))
                for stat in player_stats_dic.keys():
                    c.execute(f"UPDATE stats SET {stat} = ? WHERE name=?",(player_stats_dic[stat],name))
        conn.commit()
    conn.close()


def add_team_obl(team):
    conn = create_connection()
    if conn is not None:
        c=conn.cursor()
        opponents = sample(get_filtered_teams([team.name]), 5)
        c.execute("INSERT INTO one_big_league(team_name, current_opponent_pool) VALUES (?, ?)", (team.name, list_to_newline_string(opponents)))

        conn.commit()
    conn.close()

def save_obl_results(winning_team, losing_team):
    conn = create_connection()
    if conn is not None:
        c=conn.cursor()
        try:
            c.execute("SELECT teams_beaten_list, current_opponent_pool, obl_points FROM one_big_league WHERE team_name = ?", (winning_team.name,))
            beaten_string, opponents_string, obl_points = c.fetchone()
        except:
            return

        beaten_teams = newline_string_to_list(beaten_string)
        opponent_teams = newline_string_to_list(opponents_string)
        if re.sub('[^A-Za-z0-9 %]+', '', losing_team.name) in opponent_teams:
            beaten_teams.append(losing_team.name)
            try:
                opponent_teams = sample(get_filtered_teams([winning_team.name] + beaten_teams), 5)
            except ValueError:
                opponent_teams = get_filtered_teams([winning_team.name] + beaten_teams)
            obl_points += 1

            c.execute("UPDATE one_big_league SET teams_beaten_list = ?, current_opponent_pool = ?, obl_points = ? WHERE team_name = ?", (list_to_newline_string(beaten_teams), list_to_newline_string(opponent_teams), obl_points, winning_team.name))

        conn.commit()
        conn.close()
    return

def get_obl_stats(team, full = False):
    conn = create_connection()
    if conn is not None:
        c=conn.cursor()
        opponents_string = None
        while opponents_string is None:
            c.execute("SELECT teams_beaten_list, current_opponent_pool, rival_name FROM one_big_league WHERE team_name = ?", (team.name,))
            try:
                beaten_string, opponents_string, rival_name = c.fetchone()
            except TypeError: #add team to OBL
                add_team_obl(team)
            
        beaten_teams = newline_string_to_list(beaten_string)
        opponent_teams = opponents_string
        obl_points = len(beaten_teams)

        teams_list = [name for name, points in obl_leaderboards()]
        rank = teams_list.index(team.name) + 1
        if not full:
            return (obl_points, opponent_teams, rank)
        else:
            return (obl_points, beaten_teams, opponent_teams, rank, rival_name)
        conn.close()
    return (None, None)

def obl_leaderboards():
    conn = create_connection()
    if conn is not None:
        c=conn.cursor()
        c.execute("SELECT team_name, obl_points FROM one_big_league ORDER BY obl_points DESC")
        teams_list = c.fetchall()

        return teams_list #element (team_name, obl_points)
        conn.close()
    return False

def set_obl_rival(base_team, rival):
    conn = create_connection()
    if conn is not None:
        c=conn.cursor()

        c.execute("UPDATE one_big_league SET rival_name = ? WHERE team_name = ?", (rival.name, base_team.name))
        conn.commit()
    conn.close()

def list_to_newline_string(list):
    string = ""
    for element in list:
        if string != "":
            string += "\n"
        string += element       
    return string

def newline_string_to_list(string):
    if string is not None and string != "":
        return string.split("\n")
    else:
        return []