import discord
import json
import database as db
import os

client = discord.Client()

def config():
    if not os.path.exists("config.json"):
        #generate default config
        config_dic = {
                "token" : "",
                "owners" : [
                    0000
                    ]
            }
        with open("config.json", "w") as config_file:
            json.dump(config_dic, config_file, indent=4)
            print("please fill in bot token and any bot admin discord ids to the new config.json file!")
            quit()
    else:
        with open("config.json") as config_file:
            return json.load(config_file)

@client.event
async def on_ready():
    print(f"logged in as {client.user} with token {config()['token']}")

@client.event
async def on_message(msg):
    print(


client.run(config()["token"])