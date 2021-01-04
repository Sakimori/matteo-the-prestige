import discord, json, math, os, roman, games, asyncio, random, main_controller, threading, time, urllib, leagues
import database as db
import onomancer as ono
from flask import Flask


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
        league = None
        if config()["game_freeze"]:
            await msg.channel.send("Patch incoming. We're not allowing new games right now.")
            return

        if "-l " in command.split("\n")[0]:          
            league = command.split("\n")[0].split("-l ")[1]
        elif "--league " in command.split("\n")[0]:
            league = command.split("\n")[0].split("--league ")[1]

        innings = None
        try:
            team_name1 = command.split("\n")[1].strip()
            team1 = get_team_fuzzy_search(team_name1)

            team_name2 = command.split("\n")[2].strip()
            team2 = get_team_fuzzy_search(team_name2)

            innings = int(command.split("\n")[3])
        except IndexError:
            try:
                team_name1 = command.split("\n")[1].strip()
                team1 = get_team_fuzzy_search(team_name1)

                team_name2 = command.split("\n")[2].strip()
                team2 = get_team_fuzzy_search(team_name2)
            except IndexError:
                await msg.channel.send("We need at least three lines: startgame, away team, and home team are required. Optionally, the number of innings can go at the end, if you want a change of pace.")
                return
        except:
            await msg.channel.send("Something about that command tripped us up. Either we couldn't find a team, or you gave us a bad number of innings.")
            return

        if innings is not None and innings < 2:
            await msg.channel.send("Anything less than 2 innings isn't even an outing. Try again.")
            return 
                                                    
        elif innings is not None and innings > 200 and msg.author.id not in config()["owners"]:
            await msg.channel.send("Y'all can behave, so we've upped the limit on game length to 200 innings.")
            return

        if team1 is not None and team2 is not None:
            game = games.game(team1.finalize(), team2.finalize(), length=innings)
            channel = msg.channel
            await msg.delete()
            
            game_task = asyncio.create_task(watch_game(channel, game, user=msg.author, league=league))
            await game_task
        else:
            await msg.channel.send("We can't find one or both of those teams. Check your staging, chief.")
            return

class SaveTeamCommand(Command):
    name = "saveteam"
    template = """m;saveteam
   [name] 
   [slogan] 
   [lineup]
   [rotation]"""

    description = """Saves a team to the database allowing it to be used for games. Send this command at the top of a list, with entries separated by new lines (shift+enter in discord, or copy+paste from notepad).
  - the first line of the list is your team's name (cannot contain emoji).
  - the second line is your team's icon and slogan, this should begin with an emoji followed by a space, followed by a short slogan.
  - the third line must be blank.
  - the next lines are your batters' names in the order you want them to appear in your lineup, lineups can contain any number of batters between 1 and 12.
  - there must be another blank line between your batters and your pitchers.
  - the final lines are your pitchers' names.
if you did it correctly, you'll get a team embed with a prompt to confirm. hit the 👍 and it'll be saved."""

    async def execute(self, msg, command):
        if db.get_team(command.split('\n',1)[1].split("\n")[0]) == None:
            await msg.channel.send(f"Fetching players...")
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
        team = get_team_fuzzy_search(team_name)
        if team is not None:
            await msg.channel.send(embed=build_team_embed(team))
            return
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

class SwapPlayerCommand(Command):
    name = "swapsection"
    template = """m;swapsection
    [team name]
    [player name]"""
    description = "Swaps a player from lineup to rotation, or from rotation to lineup. Requires team ownership and exact spelling of team name."

    async def execute(self, msg, command):
        try:
            team_name = command.split("\n")[1].strip()
            player_name = command.split("\n")[2].strip()
            team, owner_id = games.get_team_and_owner(team_name)
            if team is None:
                await msg.channel.send("Can't find that team, boss. Typo?")
                return
            elif owner_id != msg.author.id and msg.author.id not in config()["owners"]:
                await msg.channel.send("You're not authorized to mess with this team. Sorry, boss.")
                return
            elif not team.swap_player(player_name):
                await msg.channel.send("Either we can't find that player, you've got no space on the other side, or they're your last member of that side of the roster. Can't field an empty lineup, and we *do* have rules, chief.")
                return
            else:
                await msg.channel.send(embed=build_team_embed(team))
                games.update_team(team)
                await msg.channel.send("Paperwork signed, stamped, copied, and faxed up to the goddess. Xie's pretty quick with this stuff.")
        except IndexError:
            await msg.channel.send("Three lines, remember? Command, then team, then name.")

class MovePlayerCommand(Command):
    name = "moveplayer"
    template = """m;moveplayer 
    [team name]
    [player name]
    [new lineup/rotation position number] (indexed with 1 being the top)"""
    description = "Moves a player in your lineup or rotation. Requires team ownership and exact spelling of team name."

    async def execute(self, msg, command):
        try:
            team_name = command.split("\n")[1].strip()
            player_name = command.split("\n")[2].strip()
            team, owner_id = games.get_team_and_owner(team_name)
            try:
                new_pos = int(command.split("\n")[3].strip())
            except ValueError:
                await msg.channel.send("Hey, quit being cheeky. We're just trying to help. Third line has to be a natural number, boss.")
                return
            if owner_id != msg.author.id and msg.author.id not in config()["owners"]:
                await msg.channel.send("You're not authorized to mess with this team. Sorry, boss.")
                return
            elif not team.slide_player(player_name, new_pos):
                await msg.channel.send("You either gave us a number that was bigger than your current roster, or we couldn't find the player on the team. Try again.")
                return
            else:
                await msg.channel.send(embed=build_team_embed(team))
                games.update_team(team)
                await msg.channel.send("Paperwork signed, stamped, copied, and faxed up to the goddess. Xie's pretty quick with this stuff.")
        except IndexError:
            await msg.channel.send("Four lines, remember? Command, then team, then name, and finally, new spot on the lineup or rotation.")

class AddPlayerCommand(Command):
    name = "addplayer"
    template = """m;addplayer pitcher (or m;addplayer batter)
    [team name]
    [player name]"""
    description = "Recruits a new player to your team, as either a pitcher or a batter. Requires team ownership and exact spelling of team name."

    async def execute(self, msg, command):
        try:
            team_name = command.split("\n")[1].strip()
            player_name = command.split("\n")[2].strip()
            team, owner_id = games.get_team_and_owner(team_name)
            if owner_id != msg.author.id and msg.author.id not in config()["owners"]:
                await msg.channel.send("You're not authorized to mess with this team. Sorry, boss.")
                return

            new_player = games.player(ono.get_stats(player_name))

            if "batter" in command.split("\n")[0]:
                if not team.add_lineup(new_player)[0]:
                    await msg.channel.send("Too many batters 🎶")
                    return
            elif "pitcher" in command.split("\n")[0]:
                if not team.add_pitcher(new_player):
                    await msg.channel.send("8 pitchers is quite enough, we think.")
                    return

            await msg.channel.send(embed=build_team_embed(team))
            games.update_team(team)
            await msg.channel.send("Paperwork signed, stamped, copied, and faxed up to the goddess. Xie's pretty quick with this stuff.")
        except IndexError:
            await msg.channel.send("Three lines, remember? Command, then team, then name.")

class RemovePlayerCommand(Command):
    name = "removeplayer"
    template = """m;removeplayer
    [team name]
    [player name]"""
    description = "Removes a player from your team. Requires team ownership and exact spelling of team name."

    async def execute(self, msg, command):
        try:
            team_name = command.split("\n")[1].strip()
            player_name = command.split("\n")[2].strip()
            team, owner_id = games.get_team_and_owner(team_name)
            if owner_id != msg.author.id and msg.author.id not in config()["owners"]:
                await msg.channel.send("You're not authorized to mess with this team. Sorry, boss.")
                return

            if not team.delete_player(player_name):
                await msg.channel.send("We've got bad news: that player isn't on your team. The good news is that... that player isn't on your team?")
                return

            else:
                await msg.channel.send(embed=build_team_embed(team))
                games.update_team(team)
                await msg.channel.send("Paperwork signed, stamped, copied, and faxed up to the goddess. Xie's pretty quick with this stuff.")
        except IndexError:
            await msg.channel.send("Three lines, remember? Command, then team, then name.")


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
    description = "Allows you to delete the team with the provided name. Requires team ownership. If you are the owner and the bot is telling you it's not yours, contact xvi and xie can assist."

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
        new_owner = msg.mentions[0]
        team_name = command.strip().split(new_owner.mention+" ")[1]
        print(team_name)
        if db.assign_owner(team_name, new_owner.id):
            await msg.channel.send(f"{team_name} is now owned by {new_owner.display_name}. Don't break it.")
        else:
            await msg.channel.send("We couldn't find that team. Typo?")

class StartTournamentCommand(Command):
    name = "starttournament"
    template = """m;starttournament
    [tournament name]
    [list of teams, each on a new line]"""
    description = "Starts a tournament with the teams given. Byes will be given to teams to allow for numbers other than powers of two. The current tournament format is:\nBest of 5 until the finals, which are Best of 7"

    async def execute(self, msg, command):
        to_parse = command.split("\n")[0]
        if "--rounddelay " in to_parse:
            try:
                round_delay = int(to_parse.split("--rounddelay ")[1].split(" ")[0])
            except ValueError:
                await msg.channel.send("The delay between rounds should be a whole number.")
                return
            if round_delay < 1 or round_delay > 120:
                await msg.channel.send("The delay between rounds has to be between 1 and 120 minutes.")
        else:
            round_delay = 10

        tourney_name = command.split("\n")[1]
        list_of_team_names = command.split("\n")[2:]
        team_dic = {}
        for name in list_of_team_names:
            team = get_team_fuzzy_search(name.strip())
            if team == None:
                await msg.channel.send(f"We couldn't find {name}. Try again?")
                return
            team_dic[team] = {"wins": 0}

        id = random.randint(1111,9999)

        tourney = leagues.tournament(tourney_name, team_dic, id=id, secs_between_rounds = round_delay * 60)
        tourney.build_bracket(random_sort = True)

        await start_tournament_round(msg.channel, tourney)


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
    SwapPlayerCommand(),
    MovePlayerCommand(),
    AddPlayerCommand(),
    RemovePlayerCommand(),
    DeleteTeamCommand(),
    ShowTeamCommand(),
    ShowAllTeamsCommand(),
    SearchTeamsCommand(),
    StartGameCommand(),
    StartTournamentCommand(),
    CreditCommand(),
    RomanCommand(),
    HelpCommand(),
]

client = discord.Client()
gamesarray = []
active_tournaments = []
setupmessages = {}

thread1 = threading.Thread(target=main_controller.update_loop)
thread1.start()

def config():
    if not os.path.exists("config.json"):
        #generate default config
        config_dic = {
                "token" : "",
                "owners" : [
                    0000
                    ],
                "prefix" : ["m;", "m!"],
                "simmadome_url" : "",
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
    watch_task = asyncio.create_task(game_watcher())
    await watch_task

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

async def watch_game(channel, newgame, user = None, league = None):
    newgame, state_init = prepare_game(newgame)

    if league is not None:
        discrim_string = league
        state_init["is_league"] = True
    elif user is not None:
        if isinstance(user, str):
            discrim_string = f"Started by {user}"
        else:
            discrim_string = f"Started by {user.name}"
        state_init["is_league"] = False
    else:
        discrim_string = "Unclaimed game."
        state_init["is_league"] = False


    timestamp = str(time.time() * 1000.0)
    ext = "?game="+timestamp
    if league is not None:
        ext += "&league=" + urllib.parse.quote_plus(league)

    await channel.send(f"{newgame.teams['away'].name} vs. {newgame.teams['home'].name}, starting at {config()['simmadome_url']+ext}")
    gamesarray.append((newgame, channel, user, timestamp))

    main_controller.master_games_dic[timestamp] = (newgame, state_init, discrim_string)

def prepare_game(newgame, league = None, weather_name = None):
    if weather_name is None:
        weathers = games.all_weathers()
        newgame.weather = weathers[random.choice(list(weathers.keys()))]

    state_init = {
        "away_name" : newgame.teams['away'].name,
        "home_name" : newgame.teams['home'].name,
        "max_innings" : newgame.max_innings,
        "update_pause" : 0,
        "top_of_inning" : True,
        "victory_lap" : False,
        "weather_emoji" : newgame.weather.emoji,
        "weather_text" : newgame.weather.name,
        "start_delay" : 5,
        "end_delay" : 10
        } 

    if league is None:
        state_init["is_league"] = False
    else:
        state_init["is_league"] = True

    if newgame.weather.name == "Heavy Snow":
        newgame.weather.counter_away = random.randint(0,len(newgame.teams['away'].lineup)-1)
        newgame.weather.counter_home = random.randint(0,len(newgame.teams['home'].lineup)-1)
    return newgame, state_init

async def start_tournament_round(channel, tourney, seeding = None):
    current_games = []
    if tourney.bracket is None:
        if seeding is None:
            tourney.build_bracket(random_sort=True)

    games_to_start = tourney.bracket.get_bottom_row()

    for pair in games_to_start:
        if pair[0] is not None and pair[1] is not None:
            this_game = games.game(pair[0].prepare_for_save().finalize(), pair[1].prepare_for_save().finalize(), length = tourney.game_length)
            this_game, state_init = prepare_game(this_game)

            state_init["is_league"] = True
            state_init["title"] = f"0 - 0"
            discrim_string = tourney.name     

            timestamp = str(time.time() * 1000.0 + random.randint(0,3000))
            current_games.append((this_game, timestamp))
            main_controller.master_games_dic[timestamp] = (this_game, state_init, discrim_string)

    ext = "?league=" + urllib.parse.quote_plus(tourney.name)

    if tourney.round_check(): #if finals
        await channel.send(f"The {tourney.name} finals are starting now, at {config()['simmadome_url']+ext}")
        finals = True
    else:
        await channel.send(f"{len(current_games)} games started for the {tourney.name} tournament, at {config()['simmadome_url']+ext}")
        finals = False
    await tourney_round_watcher(channel, tourney, current_games, config()['simmadome_url']+ext, finals)

async def continue_tournament_series(tourney, queue, games_list, wins_in_series):
    for oldgame in queue:
        away_team = games.get_team(oldgame.teams["away"].name)
        home_team = games.get_team(oldgame.teams["home"].name)
        this_game = games.game(away_team.finalize(), home_team.finalize(), length = tourney.game_length)
        this_game, state_init = prepare_game(this_game)

        state_init["is_league"] = True

        state_init["title"] = f"{wins_in_series[oldgame.teams['away'].name]} - {wins_in_series[oldgame.teams['home'].name]}"

        discrim_string = tourney.name     

        timestamp = str(time.time() * 1000.0 + random.randint(0,3000))
        games_list.append((this_game, timestamp))
        main_controller.master_games_dic[timestamp] = (this_game, state_init, discrim_string)

    return games_list

async def tourney_round_watcher(channel, tourney, games_list, filter_url, finals = False):
    tourney.active = True
    active_tournaments.append(tourney)
    wins_in_series = {}
    winner_list = []
    while tourney.active:
        queued_games = []
        while len(games_list) > 0:
            try:
                for i in range(0, len(games_list)):
                    game, key = games_list[i]
                    if game.over and main_controller.master_games_dic[key][1]["end_delay"] <= 9:
                        if game.teams['home'].name not in wins_in_series.keys():
                            wins_in_series[game.teams["home"].name] = 0
                        if game.teams['away'].name not in wins_in_series.keys():
                            wins_in_series[game.teams["away"].name] = 0

                        winner_name = game.teams['home'].name if game.teams['home'].score > game.teams['away'].score else game.teams['away'].name

                        if winner_name in wins_in_series.keys():
                            wins_in_series[winner_name] += 1
                        else:
                            wins_in_series[winner_name] = 1

                        final_embed = game_over_embed(game)
                        await channel.send(f"A {tourney.name} game just ended!")                
                        await channel.send(embed=final_embed)
                        if wins_in_series[winner_name] >= int((tourney.series_length+1)/2) and not finals:
                            winner_list.append(winner_name)
                        elif wins_in_series[winner_name] >= int((tourney.finals_length+1)/2):
                            winner_list.append(winner_name)
                        else:
                            queued_games.append(game)
                            
                        games_list.pop(i)
                        break
            except:
                print("something went wrong in tourney_watcher")
            await asyncio.sleep(4)

        
        if len(queued_games) > 0:
            await channel.send(f"The next batch of games for {tourney.name} will start in {int(tourney.delay/60)} minutes.")
            await asyncio.sleep(tourney.delay)
            await channel.send(f"{len(queued_games)} games for {tourney.name}, starting at {filter_url}")
            games_list = await continue_tournament_series(tourney, queued_games, games_list, wins_in_series)
        else:
            tourney.active = False

    if finals: #if this last round was finals
        embed = discord.Embed(color = discord.Color.dark_purple(), title = f"{winner_list[0]} win the {tourney.name} finals!")
        await channel.send(embed=embed)
        active_tournaments.pop(active_tournaments.index(tourney))
        return

    tourney.bracket.set_winners_dive(winner_list)

    winners_string = ""
    for game in tourney.bracket.get_bottom_row():
        winners_string += f"{game[0].name}\n{game[1].name}\n"
    await channel.send(f"""
This round of games for {tourney.name} is now complete! The next round will be starting in {int(tourney.round_delay/60)} minutes.
Advancing teams:
{winners_string}""")
    await asyncio.sleep(tourney.round_delay)
    await start_tournament_round(channel, tourney)



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

    rotation_string = ""
    for player in team.rotation:
        rotation_string += f"{player.name} {player.star_string('pitching_stars')}\n"
    embed.add_field(name="Rotation:", value=rotation_string, inline = False)
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
    if not len(newteam_json["rotation"]) > 8:
        raise CommandError("8 pitchers on the rotation, max. That's a *lot* of pitchers.")
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
    if not roster[2].strip() == "":
        raise CommandError("The third line should be blank. It wasn't, so just in case, we've not done anything on our end.")
    pitchernum = len(roster)-2
    for rosternum in range(3,len(roster)-1):
        if roster[rosternum] != "":
            if len(roster[rosternum]) > 70:
                raise CommandError(f"{roster[rosternum]} is too long, chief. 70 or less.")
            newteam.add_lineup(games.player(ono.get_stats(roster[rosternum].rstrip())))
        else:
            pitchernum = rosternum + 1 
            break

    for rosternum in range(pitchernum, len(roster)):
        if len(roster[rosternum]) > 70:
            raise CommandError(f"{roster[len(roster)-1]} is too long, chief. 70 or less.")
        newteam.add_pitcher(games.player(ono.get_stats(roster[rosternum].rstrip()))) 

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
                if all_teams[i+25*page].slogan.strip() != "":
                    embed.add_field(name=all_teams[i+25*page].name, value=all_teams[i+25*page].slogan)
                else:
                    embed.add_field(name=all_teams[i+25*page].name, value="404: Slogan not found")
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

async def game_watcher():
    while True:
        try:
            this_array = gamesarray.copy()
            for i in range(0,len(this_array)):
                game, channel, user, key = this_array[i]
                if game.over and main_controller.master_games_dic[key][1]["end_delay"] <= 9:                   
                    final_embed = game_over_embed(game)
                    if user is not None:
                        await channel.send(f"{user.mention}'s game just ended.")
                    else:
                        await channel.send("A game started from this channel just ended.")                
                    await channel.send(embed=final_embed)
                    gamesarray.pop(i)
                    break
        except:
            print("something broke in game_watcher")
        await asyncio.sleep(4)

def game_over_embed(game):
    title_string = f"{game.teams['away'].name} at {game.teams['home'].name} ended after {game.inning-1} innings"
    if (game.inning - 1) > game.max_innings: #if extra innings
        title_string += f" with {game.inning - (game.max_innings+1)} extra innings.\n"
    else:
        title_string += ".\n"
    title_string += game.weather.emoji + game.weather.name

    winning_team = game.teams['home'].name if game.teams['home'].score > game.teams['away'].score else game.teams['away'].name
    winstring = f"{game.teams['away'].score} to {game.teams['home'].score}\n"
    if game.victory_lap and winning_team == game.teams['home'].name:
        winstring += f"{winning_team} wins with a victory lap!"
    elif winning_team == game.teams['home'].name:
        winstring += f"{winning_team} wins, shaming {game.teams['away'].name}!"
    else:
        winstring += f"{winning_team} wins!"

    embed = discord.Embed(color=discord.Color.dark_purple(), title=title_string)
    embed.add_field(name="Final score:", value=winstring)
    return embed

def get_team_fuzzy_search(team_name):
    team = games.get_team(team_name)
    if team is None:
        teams = games.search_team(team_name.lower())
        if len(teams) == 1:
            team = teams[0]
    return team
        

#test_bracket = {
#        "Milwaukee Lockpicks" : {"wins": 4, "rd": 0},
#        "Madagascar Penguins" : {"wins": 2, "rd": 0},
#        "Twin Cities Evening" : {"wins": 1, "rd": 0},
#        "Washington State Houses" : {"wins": 9, "rd": 0},
#        "Appalachian Underground" : {"wins": 8, "rd": 0},
#        "Pacific2 Rams" : {"wins": 3, "rd": 0},
#        "New Jersey Radio" : {"wins": 11, "rd": 0},
#        "Moline Jolenes" : {"wins": 6, "rd": 0},
#        "California Commissioners" : {"wins": 10, "rd": 0},
#        "Pigeon’s Reckoning" : {"wins": 7, "rd": 0},
#        "Kernow Technologists" : {"wins": 5, "rd": 0}
#    }
#tourney = leagues.tournament("Test Tourney", test_bracket, max_innings=3)
#tourney.build_bracket(by_wins=True)
#tourney.bracket.set_winners_dive(['Twin Cities Evening','Madagascar Penguins', 'Pacific2 Rams'])
#print(tourney.bracket.this_bracket)

client.run(config()["token"])