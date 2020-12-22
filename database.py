#handles the database interactions
import os, json, datetime
import sqlite3 as sql


def create_connection():
    #create connection, create db if doesn't exist
    conn = None
    try:
        conn = sql.connect("matteo.db")
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

    if conn is not None:
        c = conn.cursor()
        c.execute(soulscream_table_check_string)
        c.execute(player_table_check_string)
        c.execute(player_stats_table_check_string)

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
            return json.loads(c.fetchone()[0])
        else:
            return False
    except:
        return False

def get_user_player(user): 
    conn = create_connection()
    player = get_user_player_conn(conn, user)
    conn.close()
    return player