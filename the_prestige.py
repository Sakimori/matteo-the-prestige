import discord, json, os, roman, games, asyncio
import database as db
import onomancer as ono

client = discord.Client()
gamesarray = []

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


    elif command == "startgame" and msg.author.id in config()["owners"]:
        game_task = asyncio.create_task(watch_game(msg.channel))
        await game_task



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

async def start_game(channel):
    msg = await channel.send("Play ball!")
    await asyncio.sleep(4)
    newgame = games.debug_game()
    gamesarray.append(newgame)
    while not newgame.over:
        state = newgame.gamestate_update_full()
        if not state.startswith("Game over"):
            await msg.edit(content=state)
        await asyncio.sleep(3)
    await channel.send(state)
    gamesarray.pop()

async def watch_game(channel):
    blank_emoji = discord.utils.get(client.emojis, id = 790899850295509053)
    empty_base = discord.utils.get(client.emojis, id = 790899850395779074)
    first_base = discord.utils.get(client.emojis, id = 790899850320543745)
    second_base = discord.utils.get(client.emojis, id = 790900139656740865)
    third_base = discord.utils.get(client.emojis, id = 790900156597403658)
    
    newgame = games.debug_game()
    embed = await channel.send("Play ball!")
    msg_top = await channel.send(f"{newgame.teams['away'].name} at ")
    msg_bot = await channel.send(f"{newgame.teams['home'].name} starting...")
    await asyncio.sleep(4)
    use_emoji_names = True
    for game in gamesarray:
        if game[1]:
            use_emoji_names = False
    gamesarray.append((newgame,use_emoji_names))
    
   
    while not newgame.over:
        state = newgame.gamestate_update_full()
        punc = ""
        if newgame.last_update[0]["defender"] != "":
            punc = "."
        new_embed = discord.Embed(color=discord.Color.purple(), title=f"{newgame.teams['away'].name} at {newgame.teams['home'].name}")
        new_embed.add_field(name=newgame.teams['away'].name, value=newgame.teams['away'].score, inline=True)
        new_embed.add_field(name=newgame.teams['home'].name, value=newgame.teams['home'].score, inline=True)
        if newgame.top_of_inning:
            new_embed.add_field(name="Inning:", value=f"🔼 {newgame.inning}", inline=True)
        else:
            new_embed.add_field(name="Inning:", value=f"🔽 {newgame.inning}", inline=True)
        new_embed.add_field(name="Outs:", value=newgame.outs, inline=True)
        new_embed.add_field(name="Pitcher:", value=newgame.get_pitcher(), inline=False)
        new_embed.add_field(name="Batter:", value=newgame.get_batter(), inline=False)
        if use_emoji_names:
            new_embed.set_footer(text="This game is using emoji names to indicate baserunners.")

        updatestring = f"{newgame.last_update[0]['batter']} {newgame.last_update[0]['text'].value} {newgame.last_update[0]['defender']}{punc} "
        if newgame.last_update[1] > 0:
                updatestring += f"{newgame.last_update[1]} runs scored!"

        new_embed.add_field(name="🏏", value=updatestring, inline=False)

        basemessage_t = str(blank_emoji)
        if newgame.bases[2] is not None:
            if use_emoji_names:
                await second_base.edit(name=newgame.bases[2].name)
            basemessage_t += str(second_base)
        else:
            basemessage_t += str(empty_base)
        
        basemessage_b = ""
        if newgame.bases[3] is not None:
            if use_emoji_names:
                await third_base.edit(name=newgame.bases[3].name)
            basemessage_b += str(third_base)
        else:
            basemessage_b += str(empty_base)
        basemessage_b += str(blank_emoji)

        if newgame.bases[1] is not None:
            if use_emoji_names:
                await first_base.edit(name=newgame.bases[1].name)
            basemessage_b += str(first_base)
        else:
            basemessage_b += str(empty_base)

        await embed.edit(content=None, embed=new_embed)
        await msg_top.edit(content=basemessage_t)
        await msg_bot.edit(content=basemessage_b)
        await asyncio.sleep(3)

    punc = ""
    if newgame.last_update[0]["defender"] != "":
        punc = "."
    final_embed = discord.Embed(color=discord.Color.dark_purple(), title=f"{newgame.teams['away'].name} at {newgame.teams['home'].name}")
    final_embed.add_field(name="Final score:", value=f"{newgame.teams['away'].score} to {newgame.teams['home'].score}")
    final_embed.add_field(name="Last update:", value=f"{newgame.last_update[0]['batter']} {newgame.last_update[0]['text'].value} {newgame.last_update[0]['defender']}{punc}" )
    await embed.edit(content=None, embed=final_embed)
    if newgame.teams['away'].score > newgame.teams['home'].score:
        await msg_top.edit(content = f"Game over!\n{newgame.teams['away'].name} wins!")
    else:
        await msg_top.edit(content = f"Game over!\n{newgame.teams['home'].name} wins!")
    
    await msg_bot.delete()
    gamesarray.pop(gamesarray.index((newgame,use_emoji_names))) #cleanup is important!
    del newgame
        



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