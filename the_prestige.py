import discord
import json
import database as db
import os
import onomancer as ono

client = discord.Client()

def config():
    if not os.path.exists("config.json"):
        #generate default config
        config_dic = {
                "token" : "",
                "owners" : [
                    0000
                    ],
                "prefix" : ["m;", "m!"],
                "soulscream channel id" : 0
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
    command = False
    for prefix in config()["prefix"]:
        if msg.content.startswith(prefix):
            command = True
            command_s = msg.content.split(prefix, 1)
    if not command:
        return

    if msg.channel.id == config()["soulscream channel id"]:
        try:
            await msg.channel.send(ono.get_stats(msg.author.nick)["soulscream"])
        except TypeError:
            await msg.channel.send(ono.get_stats(msg.author.name)["soulscream"])
        


client.run(config()["token"])