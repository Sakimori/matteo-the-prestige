import discord, json, math, os, roman, games, asyncio
import database as db
import onomancer as ono

client = discord.Client()
gamesarray = []
gamesqueue = []
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
                "soulscream channel id" : 0,
                "game_freeze" : 0
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
            await msg.channel.send("Something went wrong. Tell xvi.")

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
        
        if config()["game_freeze"]:
            await msg.channel.send("Patch incoming. We're not allowing new games right now.")
            return

        try:
            team1 = games.get_team(command.split("\n")[1])
            team2 = games.get_team(command.split("\n")[2])
            innings = int(command.split("\n")[3])
        except IndexError:
            await msg.channel.send("We need four lines: startgame, away team, home team, and the number of innings.")
            return
        except:
            await msg.channel.send("Something about that command tripped us up. Either we couldn't find a team, or you gave us a bad number of innings.")
            return

        if innings < 2:
            await msg.channel.send("Anything less than 2 innings isn't even an outing. Try again.")
            return 
                                                    
        elif innings > 30 and msg.author.id not in config()["owners"]:
            await msg.channel.send("Y'all can't behave, so we've limited games to 30 innings. Ask xvi to start it with more if you really want to.")
            return

        if team1 is not None and team2 is not None:
            game = games.game(msg.author.name, team1, team2, length=innings)
            channel = msg.channel
            user_mention = msg.author.mention
            await msg.delete()
            if len(gamesarray) >= 45:
                await channel.send(f"We're running 45 games right now, and Discord probably isn't very pleased about it. You're at #{len(gamesqueue)+1} in the list.\nWe'll ping you when it's ready, chief.")
                gamesqueue.append((channel, game, user_mention))
                return
            
            game_task = asyncio.create_task(watch_game(channel, game))
            await game_task

    elif command.startswith("setupgame"):
        if len(gamesarray) > 45:
            await msg.channel.send("We're running 45 games and we doubt Discord will be happy with any more. These edit requests don't come cheap.")
            return 
        elif config()["game_freeze"]:
            await msg.channel.send("Patch incoming. We're not allowing new games right now.")
            return

        for game in gamesarray:
            if game.name == msg.author.name:
                await msg.channel.send("You've already got a game in progress! Wait a tick, boss.")
                return
        try:
            inningmax = int(command.split("setupgame ")[1])
        except:
            inningmax = 3
        game_task = asyncio.create_task(setup_game(msg.channel, msg.author, games.game(msg.author.name, games.team(), games.team(), length=inningmax)))
        await game_task

    elif command.startswith("saveteam\n"):
        if db.get_team(command.split("\n",1)[1].split("\n")[0]) == None:
            save_task = asyncio.create_task(save_team_batch(msg, command))
            await save_task
        else:
            name = command.split('\n',1)[1].split('\n')[0]
            await msg.channel.send(f"{name} already exists. Try a new name, maybe?")

    elif command.startswith("showteam "):
        team = games.get_team(command.split(" ",1)[1])
        if team is not None:
            await msg.channel.send(embed=build_team_embed(team))
        else:
            await msg.channel.send("Can't find that team, boss. Typo?")

    elif command == ("showallteams"):
        list_task = asyncio.create_task(team_pages(msg, games.get_all_teams()))
        await list_task

    elif command.startswith("searchteams "):
        search_term = command.split("searchteams ",1)[1]
        if len(search_term) > 30:
            await msg.channel.send("Team names can't even be that long, chief. Try something shorter.")
            return
        list_task = asyncio.create_task(team_pages(msg, games.search_team(search_term), search_term=search_term))
        await list_task

    elif command == "credit":
        await msg.channel.send("Our avatar was graciously provided to us, with permission, by @HetreaSky on Twitter.")

    elif command.startswith("help"):
        command_descriptions = {
            "idolize":("m;idolize [name]", "Records any name as your idol, used elsewhere. There's a limit of 70 characters. That should be *plenty*."),
            "showidol":("m;showidol", "Displays your idol's name and stars in a nice discord embed."),
            "showplayer":("m;showplayer [name]", "Displays any name's stars in a nice discord embed."),
            "setupgame":("m;setupgame", "Begins setting up a 3-inning pickup game. Pitchers, lineups, and team names are given during the setup process by anyone able to type in that channel. Idols are easily signed up via emoji during the process. The game will start automatically after setup."),
            "saveteam":("m;saveteam", """To save an entire team, send this command at the top of a list, with lines seperated by newlines (shift+enter in discord, or copy+paste from notepad)
  - the first line of the list is your team's name (cannot contain emoji)
  - the second is your team's slogan
  - the rest of the lines are your players' names
  - the last player is designated your pitcher
if you did it correctly, you'll get a team embed with a prompt to confirm. Hit the 👍 and it'll be saved."""),
            "showteam":("m;showteam [name]", "You can view any saved team with this command"),
            "showallteams":("m;showallteams", "This displays a paginated list of all teams available for `startgame`"),
            "searchteams":("m;searchteams [searchterm]", "Displays paginated list of all teams whose names contain `searchterm`"),
            "startgame":("m;startgame", """To start a game with premade teams, use this command at the top of a list as above
  - the first line is the away team's name
  - the second is the home team's name
  - the third is the number of innings, which must be greater than 2."""),
            "credit":("m;credit", "Shows artist credit for matteo's avatar."),
            "roman":("m;roman [number]", "Converts any natural number less than 4,000,000 into roman numerals. This one is just for fun."),
            "help":("m;help [command]", "Displays a list of all commands, or the description of the given command if one is present.")
        }
        if command == "help":
            text = "Here's everything we know how to do; use `m;help [command]` for more info:"
            for name in command_descriptions:
                text += "\n  - {}".format(name)
        else:
            lookup = command[4:].strip()
            if lookup in command_descriptions:
                text = "`{}`:\n{}".format(command_descriptions[lookup][0], command_descriptions[lookup][1])
            else:
                text = "Can't find that command, boss; try checking the list with `m;help`."
        await msg.channel.send(text)

    elif command == "countactivegames" and msg.author.id in config()["owners"]:
        await msg.channel.send(f"There's {len(gamesarray)} active games right now, boss.")




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
        try:
            msg = await client.wait_for('message', timeout=120.0, check=messagecheck)
        except asyncio.TimeoutError:
            await channel.send("Game timed out. 120 seconds between players is a bit much, see?")
            del setupmessages[team_join_message]
            del newgame
            return

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
    gamesarray.append(newgame)
    pause = 0
    top_of_inning = True
    victory_lap = False

    while not newgame.over or newgame.top_of_inning != top_of_inning:
        state = newgame.gamestate_display_full()

        new_embed = discord.Embed(color=discord.Color.purple(), title=f"{newgame.teams['away'].name} at {newgame.teams['home'].name}")
        
        new_embed.add_field(name=newgame.teams['away'].name, value=newgame.teams['away'].score, inline=True)
        new_embed.add_field(name=newgame.teams['home'].name, value=newgame.teams['home'].score, inline=True)

        if top_of_inning:
            new_embed.add_field(name="Inning:", value=f"🔼 {newgame.inning} / {newgame.max_innings}", inline=True)
            new_embed.set_footer(text=f"{newgame.teams['away'].name} batting.")
        else:
            new_embed.add_field(name="Inning:", value=f"🔽 {newgame.inning} / {newgame.max_innings}", inline=True)
            new_embed.set_footer(text=f"{newgame.teams['home'].name} batting.")

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
                new_embed.set_field_at(2,name="Inning:",value=f"🔽 {newgame.inning-1} / {newgame.max_innings}")

        if pause == 1:
            if newgame.top_of_inning:
                new_embed.add_field(name="🍿", value=f"Top of {newgame.inning}. {newgame.teams['away'].name} batting!", inline=False)
            else:
                if newgame.inning >= newgame.max_innings:
                    if newgame.teams["home"].score > newgame.teams["away"].score: #if home team is winning at the bottom of the last inning
                        victory_lap = True
                new_embed.add_field(name="🍿", value=f"Bottom of {newgame.inning}. {newgame.teams['home'].name} batting!", inline=False)

        if pause != 1 and state != "Game not started.":
            punc = ""
            if newgame.last_update[0]["defender"] != "":
                punc = ". "

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
        new_embed.add_field(name="Weather:", value="🌟 Supernova", inline = False)

        await embed.edit(content=None, embed=new_embed)
        top_of_inning = newgame.top_of_inning
        if pause <= 1:
            newgame.gamestate_update_full()

        pause -= 1
        await asyncio.sleep(6)
        
    title_string = f"{newgame.teams['away'].name} at {newgame.teams['home'].name} ended after {newgame.inning-1} innings"
    if (newgame.inning - 1) > newgame.max_innings: #if extra innings
        title_string += f" with {newgame.inning - (newgame.max_innings+1)} extra innings."
    else:
        title_string += "."

    final_embed = discord.Embed(color=discord.Color.dark_purple(), title=title_string)
    
    scorestring = f"{newgame.teams['away'].score} to {newgame.teams['home'].score}\n"
    if newgame.teams['away'].score > newgame.teams['home'].score:
        scorestring += f"{newgame.teams['away'].name} wins!"
    else:
        scorestring += f"{newgame.teams['home'].name} wins"
        if victory_lap:
            scorestring += " with a victory lap!"
        else:
            scorestring += f", shaming {newgame.teams['away'].name}!"


    
    final_embed.add_field(name="Final score:", value=scorestring)
    await embed.edit(content=None, embed=final_embed)

    await embed.unpin()
    gamesarray.pop(gamesarray.index(newgame)) #cleanup is important!
    newgame.add_stats()
    del newgame
    if len(gamesqueue) > 0:
        channel, game, user_mention = gamesqueue.pop(0)
        queue_task = asyncio.create_task(play_from_queue(channel, game, user_mention))
        await queue_task

async def play_from_queue(channel, game, user_mention):
    await channel.send(f"{user_mention}, your game's ready.")
    game_task = asyncio.create_task(watch_game(channel, game))
    await game_task



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
        starnum = int(starstring[0])
        addhalf = ".5" in starstring
        embedstring += "⭐" * starnum
        if addhalf:
            embedstring += "✨"
        elif starnum == 0:  # why check addhalf twice, amirite
            embedstring += "⚪️"
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
            newteam.add_lineup(games.player(ono.get_stats(roster[rosternum].rstrip())))
    if len(roster[len(roster)-1]) > 70:
        await channel.send(f"{roster[len(roster)-1]} is too long, chief. 70 or less.")
        return
    newteam.set_pitcher(games.player(ono.get_stats(roster[len(roster)-1].rstrip()))) #last line is pitcher name

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
            games.save_team(newteam, message.author.id)
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


async def team_pages(msg, all_teams, search_term=None):
    pages = []
    page_max = math.ceil(len(all_teams)/25)
    if search_term is not None:
        title_text = f"All teams matching \"{search_term}\":"
    else:
        title_text = "All Teams"

    for page in range(0,page_max):
        embed = discord.Embed(color=discord.Color.purple(), title=title_text)
        embed.set_footer(text = f"Page {page+1} of {page_max}")
        for i in range(0,25):
            try:
                embed.add_field(name=all_teams[i+25*page].name, value=all_teams[i+25*page].slogan)
            except:
                break
        pages.append(embed)

    teams_list = await msg.channel.send(embed=pages[0])
    current_page = 0

    if page_max > 1:
        await teams_list.add_reaction("◀")
        await teams_list.add_reaction("▶")

        def react_check(react, user):
            return user == msg.author and react.message == teams_list

        while True:
            try:
                react, user = await client.wait_for('reaction_add', timeout=60.0, check=react_check)
                if react.emoji == "◀" and current_page > 0:
                    current_page -= 1
                elif react.emoji == "▶" and current_page < (page_max-1):
                    current_page += 1
                await teams_list.edit(embed=pages[current_page])
            except asyncio.TimeoutError:
                return



client.run(config()["token"])
