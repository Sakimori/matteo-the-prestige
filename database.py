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
    
    if conn is not None:
        c = conn.cursor()
        c.execute(soulscream_table_check_string)

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
