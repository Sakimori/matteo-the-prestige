import discord, json, os, roman, games, asyncio
import database as db
import onomancer as ono

client = discord.Client()
gamesarray = []
setupmessages = {}

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
async def on_reaction_add(reaction, user):
    if reaction.message in setupmessages.keys():
        game = setupmessages[reaction.message]
        try:
            if str(reaction.emoji) == "🔼" and not user == client.user:
                new_player = games.player(ono.get_stats(db.get_user_player(user)["name"]))
                game.teams["away"].add_lineup(new_player)
                await reaction.message.channel.send(f"{new_player} {new_player.star_string('batting_stars')} takes spot #{len(game.teams['away'].lineup)} on the away lineup.")
            elif str(reaction.emoji) == "🔽" and not user == client.user:
                new_player = games.player(ono.get_stats(db.get_user_player(user)["name"]))
                game.teams["home"].add_lineup(new_player)
                await reaction.message.channel.send(f"{new_player} {new_player.star_string('batting_stars')} takes spot #{len(game.teams['home'].lineup)} on the home lineup.")
        except:
            await reaction.message.channel.send(f"{user.display_name}, we can't find your idol. Maybe you don't have one yet?")

@client.event
async def on_message(msg):

    if msg.author == client.user:
        return


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
        player_name = discord.utils.escape_mentions(command.split(" ",1)[1])
        if len(player_name) >= 70:
            await msg.channel.send("That name is too long. Please keep it below 70 characters, for my sake and yours.")
            return
        try:
            player_json = ono.get_stats(player_name)
            db.designate_player(msg.author, json.loads(player_json))
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

    elif command.startswith("showplayer "):
        player_name = json.loads(ono.get_stats(command.split(" ",1)[1]))
        await msg.channel.send(embed=build_star_embed(player_name))



    elif command.startswith("startgame\n"):
        if len(gamesarray) > 45:
            await msg.channel.send("We're running 45 games and we doubt Discord will be happy with any more. These edit requests don't come cheap.")
            return

        try:
            team1 = games.get_team(command.split("\n")[1])
            team2 = games.get_team(command.split("\n")[2])
            innings = int(command.split("\n")[3])
        except IndexError:
            await msg.channel.send("We need four lines: startgame, away team, home team, and the number of innings.")
            return
        except:
            await msg.channel.send("Something about that command tripped us up. Probably the number of innings at the end?")
            return

        if innings < 2:
            await msg.channel.send("Anything less than 2 innings isn't even an outing. Try again.")
            return 

        if team1 is not None and team2 is not None:
            game = games.game(msg.author.name, team1, team2, length=innings)
            game_task = asyncio.create_task(watch_game(msg.channel, game))
            await game_task

    elif command.startswith("setupgame"):
        if len(gamesarray) > 45:
            await msg.channel.send("We're running 45 games and we doubt Discord will be happy with any more. These edit requests don't come cheap.")
            return 

        for game in gamesarray:
            if game[0].name == msg.author.name:
                await msg.channel.send("You've already got a game in progress! Wait a tick, boss.")
                return
        try:
            inningmax = int(command.split("setupgame ")[1])
        except:
            inningmax = 3
        game_task = asyncio.create_task(setup_game(msg.channel, msg.author, games.game(msg.author.name, games.team(), games.team(), length=inningmax)))
        await game_task

    elif command.startswith("saveteam\n"):
        save_task = asyncio.create_task(save_team_batch(msg, command))
        await save_task

    elif command.startswith("showteam "):
        team = games.get_team(command.split(" ",1)[1]) 
        if team is not None:
            await msg.channel.send(embed=build_team_embed(team))
        else:
            await msg.channel.send("Can't find that team, boss. Typo?")

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


async def setup_game(channel, owner, newgame):
    newgame.owner = owner
    await channel.send(f"Game sucessfully created!\nStart any commands for this game with `{newgame.name}` so I know who's talking about what.")
    await asyncio.sleep(1)
    await channel.send("Who's pitching for the away team?")

    def input(msg):
            return msg.content.startswith(newgame.name) and msg.channel == channel #if author or willing participant and in correct channel

    while newgame.teams["home"].pitcher == None:

        def nameinput(msg):
            return msg.content.startswith(newgame.name) and msg.channel == channel #if author or willing participant and in correct channel

        

        while newgame.teams["away"].pitcher == None:
            try:
                namemsg = await client.wait_for('message', check=input)
                new_pitcher_name = discord.utils.escape_mentions(namemsg.content.split(f"{newgame.name} ")[1])
                if len(new_pitcher_name) > 70:
                    await channel.send("That player name is too long, chief. 70 or less.")
                else:
                    new_pitcher = games.player(ono.get_stats(new_pitcher_name))
                    newgame.teams["away"].set_pitcher(new_pitcher)
                    await channel.send(f"{new_pitcher} {new_pitcher.star_string('pitching_stars')}, pitching for the away team!\nNow, the home team's pitcher. Same dance, folks.")
            except NameError:
                await channel.send("Uh.")

        try:
            namemsg = await client.wait_for('message', check=input)
            new_pitcher_name = discord.utils.escape_mentions(namemsg.content.split(f"{newgame.name} ")[1])
            if len(new_pitcher_name) > 70:
                await channel.send("That player name is too long, chief. 70 or less.")
            else:
                new_pitcher = games.player(ono.get_stats(new_pitcher_name))
                newgame.teams["home"].set_pitcher(new_pitcher)
                await channel.send(f"And {new_pitcher} {new_pitcher.star_string('pitching_stars')}, pitching for the home team.")
        except:
            await channel.send("Uh.")

    #pitchers assigned!
    team_join_message = await channel.send(f"""Now, the lineups! I need somewhere between 1 and 12 batters. Cloning helps a lot with this sort of thing.
React to this message with 🔼 to have your idol join the away team, or 🔽 to have them join the home team.
You can also enter names like you did for the pitchers, with a slight difference: `away [name]` or `home [name]` instead of just the name.

Creator, type `{newgame.name} done` to finalize lineups.""")
    await team_join_message.add_reaction("🔼")
    await team_join_message.add_reaction("🔽")

    setupmessages[team_join_message] = newgame

    #emoji_task = asyncio.create_task(watch_for_reacts(team_join_message, ready, newgame))
    #msg_task = asyncio.create_task(watch_for_messages(channel, ready, newgame))
    #await asyncio.gather(
    #    watch_for_reacts(team_join_message, newgame),
    #    watch_for_messages(channel, newgame)
    #    )

    def messagecheck(msg):
        return (msg.content.startswith(newgame.name)) and msg.channel == channel and msg.author != client.user

    while not newgame.ready:
        msg = await client.wait_for('message', check=messagecheck)
        new_player = None
        if msg.author == newgame.owner and msg.content == f"{newgame.name} done":
            if newgame.teams['home'].finalize() and newgame.teams['away'].finalize():
                newgame.ready = True
                break
        else:
            side = None
            if msg.content.split(f"{newgame.name} ")[1].split(" ",1)[0] == "home":
                side = "home"
            elif msg.content.split(f"{newgame.name} ")[1].split(" ",1)[0] == "away":
                side = "away"

            if side is not None:
                new_player_name = discord.utils.escape_mentions(msg.content.split(f"{newgame.name} ")[1].split(" ",1)[1])
                if len(new_player_name) > 70:
                    await channel.send("That player name is too long, chief. 70 or less.")
                else:
                    new_player = games.player(ono.get_stats(new_player_name))
        try:
            if new_player is not None:
                newgame.teams[side].add_lineup(new_player)
                await channel.send(f"{new_player} {new_player.star_string('batting_stars')} takes spot #{len(newgame.teams[side].lineup)} on the {side} lineup.")
        except:
            True

    del setupmessages[team_join_message] #cleanup!

    await channel.send("Name the away team, creator.")

    def ownercheck(msg):
        return msg.author == newgame.owner

    while newgame.teams["home"].name == None:
        while newgame.teams["away"].name == None:
            newname = await client.wait_for('message', check=ownercheck)
            if len(newname.content) < 30:
                newgame.teams['away'].name = newname.content
                await channel.send(f"Stepping onto the field, the visitors: {newname.content}!\nFinally, the home team, and we can begin.")
            else:
                await channel.send("Hey, keep these to 30 characters or less please. Discord messages have to stay short.")
        newname = await client.wait_for('message', check=ownercheck)
        if len(newname.content) < 30:
            newgame.teams['home'].name = newname.content
            await channel.send(f"Next on the diamond, your home team: {newname.content}!")
        else:
            await channel.send("Hey, keep these to 30 characters or less please. Discord messages have to stay short.")

    await asyncio.sleep(3)
    await channel.send(f"**{newgame.teams['away'].name} at {newgame.teams['home'].name}**")

    game_task = asyncio.create_task(watch_game(channel, newgame))
    await game_task

async def watch_game(channel, game):
    blank_emoji = discord.utils.get(client.emojis, id = 790899850295509053)
    empty_base = discord.utils.get(client.emojis, id = 790899850395779074)
    occupied_base = discord.utils.get(client.emojis, id = 790899850320543745)
    out_emoji = discord.utils.get(client.emojis, id = 791578957241778226)
    in_emoji = discord.utils.get(client.emojis, id = 791578957244792832)
    
    newgame = game
    embed = await channel.send("Starting...")
    await asyncio.sleep(1)
    await embed.pin()
    await asyncio.sleep(1)
    use_emoji_names = True
    for game in gamesarray:
        if game[1]:
            use_emoji_names = False
    gamesarray.append((newgame,use_emoji_names))
    pause = 0
    top_of_inning = True

    while not newgame.over or newgame.top_of_inning != top_of_inning:
        state = newgame.gamestate_display_full()

        new_embed = discord.Embed(color=discord.Color.purple(), title=f"{newgame.teams['away'].name} at {newgame.teams['home'].name}")
        new_embed.add_field(name=newgame.teams['away'].name, value=newgame.teams['away'].score, inline=True)
        new_embed.add_field(name=newgame.teams['home'].name, value=newgame.teams['home'].score, inline=True)
        if top_of_inning:
            new_embed.add_field(name="Inning:", value=f"🔼 {newgame.inning}", inline=True)
        else:
            new_embed.add_field(name="Inning:", value=f"🔽 {newgame.inning}", inline=True)
        new_embed.add_field(name="Outs:", value=f"{str(out_emoji)*newgame.outs+str(in_emoji)*(2-newgame.outs)}", inline=False)
        new_embed.add_field(name="Pitcher:", value=newgame.get_pitcher(), inline=False)
        new_embed.add_field(name="Batter:", value=newgame.get_batter(), inline=False)

        if state == "Game not started.":
            new_embed.add_field(name="🍿", value="Play blall!", inline=False)
        
        elif newgame.top_of_inning != top_of_inning:
            pause = 2
            new_embed.set_field_at(4, name="Pitcher:", value="-", inline=False)
            new_embed.set_field_at(5, name="Batter:", value="-", inline=False)
            if newgame.top_of_inning:
                new_embed.set_field_at(2,name="Inning:",value=f"🔽 {newgame.inning-1}")

        if pause == 1:
            if newgame.top_of_inning:
                new_embed.add_field(name="🍿", value=f"Top of {newgame.inning}. {newgame.teams['away'].name} batting!", inline=False)
            else:
                new_embed.add_field(name="🍿", value=f"Bottom of {newgame.inning}. {newgame.teams['home'].name} batting!", inline=False)
        
        if pause != 1 and state != "Game not started.":
            punc = ""
            if newgame.last_update[0]["defender"] != "":
                punc = "."          

            updatestring = f"{newgame.last_update[0]['batter']} {newgame.last_update[0]['text'].value} {newgame.last_update[0]['defender']}{punc}"
            if newgame.last_update[1] > 0:
                    updatestring += f"{newgame.last_update[1]} runs scored!"

            new_embed.add_field(name="🏏", value=updatestring, inline=False)

        basemessage = str(blank_emoji)
        if newgame.bases[2] is not None:
            basemessage += str(occupied_base) + "\n"
        else:
            basemessage += str(empty_base) + "\n"
        
        basemessage_b = ""
        if newgame.bases[3] is not None:
            basemessage += str(occupied_base)
        else:
            basemessage += str(empty_base)
        basemessage += str(blank_emoji)

        if newgame.bases[1] is not None:
            basemessage += str(occupied_base)
        else:
            basemessage += str(empty_base)

        new_embed.add_field(name="Bases:", value=basemessage, inline = False)

        await embed.edit(content=None, embed=new_embed)  
        top_of_inning = newgame.top_of_inning
        if pause <= 1:
            newgame.gamestate_update_full()
        
        pause -= 1
        await asyncio.sleep(6)
        
    final_embed = discord.Embed(color=discord.Color.dark_purple(), title=f"{newgame.teams['away'].name} at {newgame.teams['home'].name}")
    
    scorestring = f"{newgame.teams['away'].score} to {newgame.teams['home'].score}\n"
    if newgame.teams['away'].score > newgame.teams['home'].score:
        scorestring += f"{newgame.teams['away'].name} wins!"
    else:
        scorestring += f"{newgame.teams['home'].name} wins!"

    final_embed.add_field(name="Final score:", value=scorestring)
    await embed.edit(content=None, embed=final_embed)
    
    await embed.unpin()
    gamesarray.pop(gamesarray.index((newgame,use_emoji_names))) #cleanup is important!
    del newgame
        
def build_team_embed(team):
    embed = discord.Embed(color=discord.Color.purple(), title=team.name)
    lineup_string = ""
    for player in team.lineup:
        lineup_string += f"{player.name} {player.star_string('batting_stars')}\n"

    embed.add_field(name="Pitcher:", value=f"{team.pitcher.name} {team.pitcher.star_string('pitching_stars')}", inline = False)
    embed.add_field(name="Lineup:", value=lineup_string, inline = False)
    embed.set_footer(text=team.slogan)
    return embed

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


async def save_team_batch(message, command):
    newteam = games.team()
    #try:
    roster = command.split("\n",1)[1].split("\n")
    newteam.name = roster[0] #first line is team name
    newteam.slogan = roster[1] #second line is slogan
    for rosternum in range(2,len(roster)-1):
        if roster[rosternum] != "":
            if len(roster[rosternum]) > 70:
                await channel.send(f"{roster[rosternum]} is too long, chief. 70 or less.")
                return
            newteam.add_lineup(games.player(ono.get_stats(roster[rosternum])))
    if len(roster[len(roster)-1]) > 70:
        await channel.send(f"{roster[len(roster)-1]} is too long, chief. 70 or less.")
        return
    newteam.set_pitcher(games.player(ono.get_stats(roster[len(roster)-1]))) #last line is pitcher name

    if len(newteam.name) > 30:
        await message.channel.send("Team names have to be less than 30 characters! Try again.")
        return
    elif len(newteam.slogan) > 100:
        await message.channel.send("We've given you 100 characters for the slogan. Discord puts limits on us and thus, we put limits on you. C'est la vie.")
        return

    await message.channel.send(embed=build_team_embed(newteam))
    checkmsg = await message.channel.send("Does this look good to you, boss?")
    await checkmsg.add_reaction("👍")
    await checkmsg.add_reaction("👎")

    def react_check(react, user):
        return user == message.author and react.message == checkmsg

    try:
        react, user = await client.wait_for('reaction_add', timeout=20.0, check=react_check)
        if react.emoji == "👍":
            await message.channel.send("You got it, chief. Saving now.")
            games.save_team(newteam)
            await message.channel.send("Saved! Thank you for flying Air Matteo. We hope you had a pleasant data entry.")
            return
        elif react.emoji == "👎":
            await message.channel.send("Message received. Pumping brakes, turning this car around. Try again, chief.")
            return
    except asyncio.TimeoutError:
        await message.channel.send("Look, I don't have all day. 20 seconds is long enough, right? Try again.")
        return
    #except:
        #await message.channel.send("uh.")
client.run(config()["token"])