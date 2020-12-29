import discord, json, math, os, roman, games, asyncio, random
import database as db
import onomancer as ono

class Command:
    def isauthorized(self, user):
        return True

    async def execute(self, msg, command):
        return

class CommandError(Exception):
    pass

class IntroduceCommand(Command):
    name = "introduce"
    template = ""
    description = ""

    def isauthorized(self, user):
        return user.id in config()["owners"]

    async def execute(self, msg, command):
        text = """**Your name, favorite team, and pronouns**: Matteo Prestige, CHST, they/them ***only.*** There's more than one of us up here, after all.
**What are you majoring in (wrong answers only)**: Economics.
**Your favorite and least favorite beverage, without specifying which**: Vanilla milkshakes, chocolate milkshakes.
**Favorite non-Mild Low team**: The Mills. We hope they're treating Ren alright.
**If you were a current blaseball player, who would you be**: We refuse to answer this question.
**Your hobbies/interests**: Minigolf, blaseball, felony insider trading.
Our avatar was graciously provided to us, with permission, by @HetreaSky on Twitter.
"""
        await msg.channel.send(text)

class CountActiveGamesCommand(Command):
    name = "countactivegames"
    template = ""
    description = ""

    def isauthorized(self, user):
        return user.id in config()["owners"]

    async def execute(self, msg, command):
        await msg.channel.send(f"There's {len(gamesarray)} active games right now, boss.")

class RomanCommand(Command):
    name = "roman"
    template = "m;roman [number]"
    description = "Converts any natural number less than 4,000,000 into roman numerals. This one is just for fun."

    async def execute(self, msg, command):
        try:
            await msg.channel.send(roman.roman_convert(command))
        except ValueError:
            await msg.channel.send(f"\"{command}\" isn't an integer in Arabic numerals.")

class IdolizeCommand(Command):
    name = "idolize"
    template = "m;idolize [name]"
    description = "Records any name as your idol, mostly for fun. There's a limit of 70 characters. That should be *plenty*."

    async def execute(self, msg, command):
        if (command.startswith("meme")):
            meme = True
            command = command.split(" ",1)[1]
        else:
            meme = False

        player_name = discord.utils.escape_mentions(command)
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

class ShowIdolCommand(Command):
    name = "showidol"
    template = "m;showidol"
    description = "Displays your idol's name and stars in a nice discord embed."

    async def execute(self, msg, command):
        try:
            player_json = db.get_user_player(msg.author)
            embed=build_star_embed(player_json)
            embed.set_footer(text=msg.author.display_name)
            await msg.channel.send(embed=embed)
        except:
            await msg.channel.send("We can't find your idol. Looked everywhere, too.")

class ShowPlayerCommand(Command):
    name = "showplayer"
    template = "m;showplayer [name]"
    description = "Displays any name's stars in a nice discord embed, there's a limit of 70 characters. That should be *plenty*. Note: if you want to lookup a lot of different players you can do it on onomancer instead of spamming this command a bunch and clogging up discord: https://onomancer.sibr.dev/reflect"

    async def execute(self, msg, command):
        player_name = json.loads(ono.get_stats(command.split(" ",1)[1]))
        await msg.channel.send(embed=build_star_embed(player_name))

class StartGameCommand(Command):
    name = "startgame"
    template = "m;startgame [away] [home] [innings]"
    description ="""Starts a game with premade teams made using saveteam, use this command at the top of a list followed by each of these in a new line (shift+enter in discord, or copy+paste from notepad):
  - the away team's name.
  - the home team's name.
  - and finally, optionally, the number of innings, which must be greater than 2 and less than 31. if not included it will default to 9."""

    async def execute(self, msg, command):
        if config()["game_freeze"]:
            await msg.channel.send("Patch incoming. We're not allowing new games right now.")
            return

        try:
            team1 = games.get_team(command.split("\n")[1])
            team2 = games.get_team(command.split("\n")[2])
            innings = int(command.split("\n")[3])
        except IndexError:
            try:
                team1 = games.get_team(command.split("\n")[1])
                team2 = games.get_team(command.split("\n")[2])
                innings = None
            except IndexError:
                await msg.channel.send("We need at least three lines: startgame, away team, and home team are required. Optionally, the number of innings can go at the end, if you want a change of pace.")
                return
        except:
            await msg.channel.send("Something about that command tripped us up. Either we couldn't find a team, or you gave us a bad number of innings.")
            return

        if innings is not None and innings < 2:
            await msg.channel.send("Anything less than 2 innings isn't even an outing. Try again.")
            return 
                                                    
        elif innings is not None and innings > 30 and msg.author.id not in config()["owners"]:
            await msg.channel.send("Y'all can't behave, so we've limited games to 30 innings. Ask xvi to start it with more if you really want to.")
            return

        if team1 is not None and team2 is not None:
            game = games.game(msg.author.name, team1, team2, length=innings)
            channel = msg.channel
            user_mention = msg.author.mention
            await msg.delete()
            if len(gamesarray) >= 10:
                await channel.send(f"We're running 10 games right now, and Discord probably isn't very pleased about it. You're at #{len(gamesqueue)+1} in the list.\nWe'll ping you when it's ready, chief.")
                gamesqueue.append((channel, game, user_mention))
                return
            
            game_task = asyncio.create_task(watch_game(channel, game, user=msg.author))
            await game_task

class SetupGameCommand(Command):
    name = "setupgame"
    template = "m;setupgame"
    description =  "Begins setting up a 3-inning pickup game. Pitchers, lineups, and team names are given during the setup process by anyone able to type in that channel. Idols are easily signed up via emoji during the process. The game will start automatically after setup."

    async def execute(self, msg, command):
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
            inningmax = int(command)
        except:
            inningmax = 3
        game_task = asyncio.create_task(setup_game(msg.channel, msg.author, games.game(msg.author.name, games.team(), games.team(), length=inningmax)))
        await game_task

class SaveTeamCommand(Command):
    name = "saveteam"
    template = "m;saveteam [name] [slogan] [players]"
    description = """Saves a team to the database allowing it to be used for games. Send this command at the top of a list, with entries separated by new lines (shift+enter in discord, or copy+paste from notepad).
  - the first line of the list is your team's name (cannot contain emoji).
  - the second line is your team's icon and slogan, this should begin with an emoji followed by a space, followed by a short slogan.
  - the next lines are your batters' names in the order you want them to appear in your lineup, lineups can contain any number of batters between 1 and 12.
  - the final line is your pitcher's name.
if you did it correctly, you'll get a team embed with a prompt to confirm. hit the 👍 and it'll be saved."""

    async def execute(self, msg, command):
        if db.get_team(command.split('\n',1)[1].split("\n")[0]) == None:
            team = team_from_message(command)
            save_task = asyncio.create_task(save_team_confirm(msg, team))
            await save_task
        else:
            name = command.split('\n',1)[1].split('\n')[0]
            await msg.channel.send(f"{name} already exists. Try a new name, maybe?")

class ImportCommand(Command):
    name = "import"
    template = "m;import [onomancer collection URL]"
    description = "Imports an onomancer collection as a new team. You can use the new onomancer simsim setting to ensure compatibility."

    async def execute(self, msg, command):
        team_raw = ono.get_collection(command.strip())
        if not team_raw == None:
            team_json = json.loads(team_raw)
            if db.get_team(team_json["fullName"]) == None:
                team = team_from_collection(team_json)
                await asyncio.create_task(save_team_confirm(msg, team))
            else:
                await msg.channel.send(f"{team_json['fullName']} already exists. Try a new name, maybe?")
        else:
            await msg.channel.send("Something went pear-shaped while we were looking for that collection. You certain it's a valid onomancer URL?")

class ShowTeamCommand(Command):
    name = "showteam"
    template = "m;showteam [name]"
    description = "Shows information about any saved team."
    
    async def execute(self, msg, command):
        team_name = command.strip()
        team = games.get_team(team_name)
        if team is not None:
            await msg.channel.send(embed=build_team_embed(team))
        else:
            teams = games.search_team(team_name.lower())
            if len(teams) == 1:
                await msg.channel.send(embed=build_team_embed(teams[0]))
            else:
                await msg.channel.send("Can't find that team, boss. Typo?")

class ShowAllTeamsCommand(Command):
    name = "showallteams"
    template = "m;showallteams" 
    description = "Shows a paginated list of all teams available for games which can be scrolled through."

    async def execute(self, msg, command):
        list_task = asyncio.create_task(team_pages(msg, games.get_all_teams()))
        await list_task

class SearchTeamsCommand(Command):
    name = "searchteams"
    template = "m;searchteams [searchterm]"
    description = "Shows a paginated list of all teams whose names contain the given search term."

    async def execute(self, msg, command):
        search_term = command.strip()
        if len(search_term) > 30:
            await msg.channel.send("Team names can't even be that long, chief. Try something shorter.")
            return
        list_task = asyncio.create_task(team_pages(msg, games.search_team(search_term), search_term=search_term))
        await list_task

class CreditCommand(Command):
    name = "credit"
    template = "m;credit"
    description = "Shows artist credit for matteo's avatar."

    async def execute(self, msg, command):
        await msg.channel.send("Our avatar was graciously provided to us, with permission, by @HetreaSky on Twitter.")

class HelpCommand(Command):
    name = "help"
    template = "m;help [command]"
    description = "Shows the instructions from the readme for a given command. If no command is provided, we will instead provide a list of all of the commands that instructions can be provided for."

    async def execute(self, msg, command):
        query = command.strip()
        if query == "":
            text = "Here's everything we know how to do; use `m;help [command]` for more info:"
            for comm in commands:
                if comm.isauthorized(msg.author):
                    text += f"\n  - {comm.name}"
        else:
            try:
                comm = next(c for c in commands if c.name == query and c.isauthorized(msg.author))
                text = f"`{comm.template}`\n{comm.description}"
            except:
                text = "Can't find that command, boss; try checking the list with `m;help`."
        await msg.channel.send(text)

class DeleteTeamCommand(Command):
    name = "deleteteam"
    template = "m;deleteteam [name]"
    description = "Allows you to delete the team with the provided name if you are the owner of it, Gives a confirmation first to prevent accidental deletions. If it isn't letting you delete your team, you probably created it before teams having owners was a thing, contact xvi and xie can assign you as the owner."

    async def execute(self, msg, command):
        team_name = command.strip()
        team, owner_id = games.get_team_and_owner(team_name)
        if owner_id != msg.author.id and msg.author.id not in config()["owners"]: #returns if person is not owner and not bot mod
            await msg.channel.send("That team ain't yours, chief. If you think that's not right, bug xvi about deleting it for you.")
            return
        elif team is not None:
            delete_task = asyncio.create_task(team_delete_confirm(msg.channel, team, msg.author))
            await delete_task

class AssignOwnerCommand(Command):
    name = "assignowner"
    template = "m;assignowner [mention] [team]"
    description = "assigns a discord user as the owner for a team."

    def isauthorized(self, user):
        return user.id in config()["owners"]

    async def execute(self, msg, command):
        #try:
        new_owner = msg.mentions[0]
        team_name = command.strip().split(new_owner.mention+" ")[1]
        print(team_name)
        if db.assign_owner(team_name, new_owner.id):
            await msg.channel.send(f"{team_name} is now owned by {new_owner.display_name}. Don't break it.")
        else:
            await msg.channel.send("We couldn't find that team. Typo?")
        #except:
            #await msg.channel.send("We hit a snag. Tell xvi.")

class ScheduleSeriesManuallyCommand():
    name = "scheduleseriesmanually"
    template = "m;scheduleseriesmanually [minutesToWaitBetweenGames] [awayTeam] @[homeTeam]"
    description = "Runs a series of games between specified teams."
    max_games_at_once = 5 # number of simultaneous games this series will attempt to run
    global_game_cap = 7 # do not schedule any games if there are more than this number of games

    def isauthorized(self, user):
        return user.id in config()["owners"]

    async def startgame(self, msg, team1, team2, innings):
        game = games.game(msg.author.name, team1, team2, length=innings)
        channel = msg.channel
        user_mention = msg.author.mention
        game_task = asyncio.create_task(watch_game(channel, game, user=msg.author))
        await game_task

    async def execute(self, msg, command):
        command = command.strip().split("\n")
        if len(command) == 0:
            await channel.send("Not a very exciting series, but sure! \n ...aand it's done! Nobody won, but nobody lost either.")
        if len(command) % 2 == 1:
            await channel.send(f"I need a number of minutes to wait between games, then an even number of teams. Are you missing a team name somewhere?")
            return

        delay_between_match_start_attempts = 60
        configLine = command[1].strip().split(" ")
        if configLine[0].isnumeric() and int(configLine[0]) > 2:
            delay_between_match_start_attempts = int(configLine[0])*60
        else:
            await channel.send("The second line should be the interval each game should start at! Maybe 5 minutes?")

        # optional: number of innings
        innings = 9
        if len(configLine) > 2:
            if configLine[1].isnumeric():
                innings = int(configLine[1])
                innings = max(3,min(innings, 30))
            else:
                await channel.send(f"{configLine[1]} doesn't sound like a valid number of innings?")
        
        # parse team pairs of team1\n@team2
        teamPairLines = command[2:]
        teamPairs = []
        for i in range(0,len(teamPairLines), 2):
            awayTeam = teamPairLines[i]
            homeTeam = teamPairLines[i+1]
            if len(homeTeam) > 2 and homeTeam[0:2] == "@ ":
                homeTeam = homeTeam[2:].strip()
            teamPairs.append((awayTeam, homeTeam))

        # to do: validate each team name
        
        gametasks = []
        num_games_started = 0
        num_games_in_series = len(teamPairs)

        notified_about_delay = False
        
        while num_games_started < num_games_in_series:
            if len(gamesarray) > self.global_game_cap:
                # There's too many simultaneous games going on right now!
                if not notified_about_delay:
                    await channel.send("We're limiting the number of simultaneous games to avoid hitting Discord limits, and there's too many games right now. Hang tight and we'll let you know when there's a spot in the queue open.")
                    notified_about_delay = True
            else:
                num_possible_game_slots = min(self.global_game_cap - len(gamesarray), self.max_games_at_once)
                for i in range(num_possible_game_slots):
                    # attempt to start another game
                    awayTeam, homeTeam = teamPairs[num_games_started]
                    game = asyncio.ensure_future(self.startgame(msg, awayTeam, homeTeam, innings))
                    gametasks.append(game)
                    notified_about_delay = False # if another delay happens, let the users know about it

                    num_games_started += 1
                    if num_games_started >= num_games_in_series:
                        break
            await asyncio.sleep(delay_between_match_start_attempts)
        #every game has been started, wait for them to end
        await asyncio.gather(*gametasks)


commands = [
    IntroduceCommand(),
    CountActiveGamesCommand(),
    AssignOwnerCommand(),
    IdolizeCommand(),
    ShowIdolCommand(),
    ShowPlayerCommand(),
    #SetupGameCommand(),
    SaveTeamCommand(),
    ImportCommand(),
    DeleteTeamCommand(),
    ShowTeamCommand(),
    ShowAllTeamsCommand(),
    SearchTeamsCommand(),
    StartGameCommand(),
    ScheduleSeriesManuallyCommand(),
    CreditCommand(),
    RomanCommand(),
    HelpCommand(),
]

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

    if msg.channel.id == config()["soulscream channel id"]:
        await msg.channel.send(ono.get_scream(msg.author.display_name))
    else:
        try:
            comm = next(c for c in commands if command.startswith(c.name))
            await comm.execute(msg, command[len(comm.name):])
        except StopIteration:
            await msg.channel.send("Can't find that command, boss; try checking the list with `m;help`.")
        except CommandError as ce:
            await msg.channel.send(str(ce))

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
    await channel.send(f"Game sucessfully created!\nStart any commands for this game with `{newgame.name}` so we know who's talking about what.")
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
    team_join_message = await channel.send(f"""Now, the lineups! We need somewhere between 1 and 12 batters. Cloning helps a lot with this sort of thing.
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

async def watch_game(channel, newgame, user = None):
    blank_emoji = discord.utils.get(client.emojis, id = 790899850295509053)
    empty_base = discord.utils.get(client.emojis, id = 790899850395779074)
    occupied_base = discord.utils.get(client.emojis, id = 790899850320543745)
    out_emoji = discord.utils.get(client.emojis, id = 791578957241778226)
    in_emoji = discord.utils.get(client.emojis, id = 791578957244792832)

    if user is not None:
        await channel.send(f"Game for {user.mention}:")
    embed = await channel.send("Starting...")
    await asyncio.sleep(1)
    await embed.pin()
    await asyncio.sleep(1)
    gamesarray.append(newgame)
    pause = 0
    top_of_inning = True
    victory_lap = False

    weathers = games.all_weathers()
    newgame.weather = weathers[random.choice(list(weathers.keys()))]

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
            if "steals" in newgame.last_update[0].keys():
                updatestring = ""
                for attempt in newgame.last_update[0]["steals"]:
                    updatestring += attempt + "\n"

                new_embed.add_field(name="💎", value=updatestring, inline=False)

            else:
                updatestring = ""
                punc = ""
                if newgame.last_update[0]["defender"] != "":
                    punc = ". "

                if "fc_out" in newgame.last_update[0].keys():
                    name, base_string = newgame.last_update[0]['fc_out']
                    updatestring = f"{newgame.last_update[0]['batter']} {newgame.last_update[0]['text'].value.format(name, base_string)} {newgame.last_update[0]['defender']}{punc}"
                else:
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
        new_embed.add_field(name="Weather:", value=str(newgame.weather), inline = False)

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

async def team_delete_confirm(channel, team, owner):
    team_msg = await channel.send(embed=build_team_embed(team))
    checkmsg = await channel.send("Is this the team you want to axe, boss?")
    await checkmsg.add_reaction("👍")
    await checkmsg.add_reaction("👎")

    def react_check(react, user):
        return user == owner and react.message == checkmsg

    try:
        react, user = await client.wait_for('reaction_add', timeout=20.0, check=react_check)
        if react.emoji == "👍":
            await channel.send("Step back, this could get messy.")
            if db.delete_team(team):
                await asyncio.sleep(2)
                await channel.send("Job's done. We'll clean up on our way out, don't worry.")
            else:
                await asyncio.sleep(2)
                await channel.send("Huh. Didn't quite work. Tell xvi next time you see xer.")
            return
        elif react.emoji == "👎":
            await channel.send("Message received. Pumping brakes, turning this car around.")
            return
    except asyncio.TimeoutError:
        await channel.send("Guessing you got cold feet, so we're putting the axe away. Let us know if we need to fetch it again, aye?")
        return


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

def team_from_collection(newteam_json):
    # verify collection against our own restrictions
    if len(newteam_json["fullName"]) > 30:
        raise CommandError("Team names have to be less than 30 characters! Try again.")
    if len(newteam_json["slogan"]) > 100:
        raise CommandError("We've given you 100 characters for the slogan. Discord puts limits on us and thus, we put limits on you. C'est la vie.")
    if len(newteam_json["lineup"]) > 20:
        raise CommandError("20 players in the lineup, maximum. We're being really generous here.")
    if not len(newteam_json["rotation"]) == 1:
        raise CommandError("One and only one pitcher per team, thanks.")
    for player in newteam_json["lineup"] + newteam_json["rotation"]:
        if len(player["name"]) > 70:
            raise CommandError(f"{player['name']} is too long, chief. 70 or less.")

    #actually build the team
    newteam = games.team()
    newteam.name = newteam_json["fullName"]
    newteam.slogan = newteam_json["slogan"]
    for player in newteam_json["lineup"]:
        newteam.add_lineup(games.player(json.dumps(player)))
    newteam.set_pitcher(games.player(json.dumps(newteam_json["rotation"][0])))

    return newteam

def team_from_message(command):
    newteam = games.team()
    roster = command.split("\n",1)[1].split("\n")
    newteam.name = roster[0] #first line is team name
    newteam.slogan = roster[1] #second line is slogan
    for rosternum in range(2,len(roster)-1):
        if roster[rosternum] != "":
            if len(roster[rosternum]) > 70:
                raise CommandError(f"{roster[rosternum]} is too long, chief. 70 or less.")
            newteam.add_lineup(games.player(ono.get_stats(roster[rosternum].rstrip())))
    if len(roster[len(roster)-1]) > 70:
        raise CommandError(f"{roster[len(roster)-1]} is too long, chief. 70 or less.")
    newteam.set_pitcher(games.player(ono.get_stats(roster[len(roster)-1].rstrip()))) #last line is pitcher name

    if len(newteam.name) > 30:
        raise CommandError("Team names have to be less than 30 characters! Try again.")
    elif len(newteam.slogan) > 100:
        raise CommandError("We've given you 100 characters for the slogan. Discord puts limits on us and thus, we put limits on you. C'est la vie.")

    return newteam

async def save_team_confirm(message, newteam):
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
        await message.channel.send("Look, we don't have all day. 20 seconds is long enough, right? Try again.")
        return

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
                    await react.remove(user)
                elif react.emoji == "▶" and current_page < (page_max-1):
                    current_page += 1
                    await react.remove(user)
                await teams_list.edit(embed=pages[current_page])
            except asyncio.TimeoutError:
                return



client.run(config()["token"])
