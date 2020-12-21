import discord, json, os, roman, games
import database as db
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
    db.initialcheck()
    print(f"logged in as {client.user} with token {config()['token']}")

@client.event
async def on_message(msg):
    command_b = False
    for prefix in config()["prefix"]:
        if msg.content.startswith(prefix):
            command_b = True
            command = msg.content.split(prefix, 1)[1]
    if not command_b:
        return

    if msg.author.id in config()["owners"] and command == "introduce":
        await introduce(msg.channel)

    elif msg.channel.id == config()["soulscream channel id"]:
        try:
            await msg.channel.send(ono.get_scream(msg.author.nick))
        except TypeError or AttributeError:
            await msg.channel.send(ono.get_scream(msg.author.name))
        except AttributeError:
            await msg.channel.send(ono.get_scream(msg.author.name))

    elif command.startswith("roman "):
        possible_int_string = command.split(" ",1)[1]
        try:
            await msg.channel.send(roman.roman_convert(possible_int_string))
        except ValueError:
            await msg.channel.send(f"\"{possible_int_string}\" isn't an integer in Arabic numerals.")

    elif command.startswith("idolize"):
        if (command.startswith("idolizememe")):
            meme = True
        else:
            meme = False
        player_name = command.split(" ",1)[1]
        try:
            player_json = ono.get_stats(player_name)
            db.designate_player(msg.author, player_json)
            if not meme:
                await msg.channel.send(f"{player_name} is now your idol.")
            else:
                await msg.channel.send(f"{player_name} is now {msg.author.display_name}'s idol.")
                await msg.channel.send(f"Reply if {player_name} is your idol also.")
        except:
            await msg.channel.send("Something went wrong. Tell 16.")

    elif command == "showidol":
        try:
            player_json = db.get_user_player(msg.author)
            embed=build_star_embed(player_json)
            embed.set_footer(text=msg.author.display_name)
            await msg.channel.send(embed=embed)
        except:
            await msg.channel.send("We can't find your idol. Looked everywhere, too.")

    elif command == "testab":
        team1 = games.team()
        team2 = games.team()
        team1.add_lineup(games.player(json.dumps(ono.get_stats("xvi"))))
        team1.set_pitcher(games.player(json.dumps(ono.get_stats("16"))))
        team1.finalize()
        team2.add_lineup(games.player(json.dumps(ono.get_stats("artemis"))))
        team2.set_pitcher(games.player(json.dumps(ono.get_stats("alphy"))))
        team2.finalize()

        game = games.game(team1, team2)
        batter = game.get_batter()
        atbat = game.at_bat()
        try:
            await msg.channel.send(f"{batter.name} {atbat['text'].value} {atbat['defender'].name}.")
        except KeyError:
            await msg.channel.send(f"{batter.name} {atbat['text'].value}")

    elif command == "credit":
        await msg.channel.send("Our avatar was graciously provided to us, with permission, by @HetreaSky on Twitter.")


async def introduce(channel):
    text = """**Your name, favorite team, and pronouns**: Matteo Prestige, CHST, they/them ***only.*** There's more than one of us up here, after all.
**What are you majoring in (wrong answers only)**: Economics.
**Your favorite and least favorite beverage, without specifying which**: Vanilla milkshakes, chocolate milkshakes.
**Favorite non-Mild Low team**: The Mills. We hope they're treating Ren alright.
**If you were a current blaseball player, who would you be**: We refuse to answer this question.
**Your hobbies/interests**: Minigolf, blaseball, felony insider trading.
Our avatar was graciously provided to us, with permission, by @HetreaSky on Twitter.
"""
    await channel.send(text)


def build_star_embed(player_json):
    starkeys = {"batting_stars" : "Batting", "pitching_stars" : "Pitching", "baserunning_stars" : "Baserunning", "defense_stars" : "Defense"}
    embed = discord.Embed(color=discord.Color.purple(), title=player_json["name"])
    for key in starkeys.keys():
        embedstring = ""
        starstring = str(player_json[key])
        if ".5" in starstring:
            starnum = int(starstring[0])
            addhalf = True
        else:
            starnum = int(player_json[key])
            addhalf = False
        embedstring += "⭐" * starnum
        if addhalf:
            embedstring += "✨"
        embed.add_field(name=starkeys[key], value=embedstring, inline=False)
    return embed



client.run(config()["token"])