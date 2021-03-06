import discord, json, math, os, roman, games, asyncio, random, main_controller, threading, time, urllib, leagues, datetime
import database as db
import onomancer as ono
from league_storage import league_exists, season_save, season_restart
from the_draft import Draft, DRAFT_ROUNDS
from flask import Flask
from uuid import uuid4
import weather

data_dir = "data"
config_filename = os.path.join(data_dir, "config.json")

class Command:
    def isauthorized(self, user):
        return True

    async def execute(self, msg, command):
        return

class DraftError(Exception):
    pass

class SlowDraftError(DraftError):
    pass

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

        player_name = discord.utils.escape_mentions(command.strip())
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
    description = "Displays any name's stars in a nice discord embed, there's a limit of 70 characters. That should be *plenty*. Note: if you want to lookup a lot of different players you can do it on onomancer here instead of spamming this command a bunch and clogging up discord: <https://onomancer.sibr.dev/reflect>"

    async def execute(self, msg, command):
        player_name = json.loads(ono.get_stats(command.split(" ",1)[1]))
        await msg.channel.send(embed=build_star_embed(player_name))

class StartGameCommand(Command):
    name = "startgame"
    template = "m;startgame [away] [home] [innings]"
    description ="""Starts a game with premade teams made using saveteam, use this command at the top of a list followed by each of these in a new line (shift+enter in discord, or copy+paste from notepad):
  - the away team's name.
  - the home team's name.
  - and finally, optionally, the number of innings, which must be greater than 2 and less than 201. if not included it will default to 9. 
  - this command has fuzzy search so you don't need to type the full name of the team as long as you give enough to identify the team you're looking for."""

    async def execute(self, msg, command):
        league = None
        day = None
        if config()["game_freeze"]:
            await msg.channel.send("Patch incoming. We're not allowing new games right now.")
            return

        if "-l " in command.split("\n")[0]:          
            league = command.split("\n")[0].split("-l ")[1].split("-")[0].strip()
        elif "--league " in command.split("\n")[0]:
            league = command.split("\n")[0].split("--league ")[1].split("-")[0].strip()
        try:
            if "-d " in command.split("\n")[0]:
                day = int(command.split("\n")[0].split("-d ")[1].split("-")[0].strip())
            elif "--day " in command.split("\n")[0]:
                day = int(command.split("\n")[0].split("--day ")[1].split("-")[0].strip())
        except ValueError:
            await msg.channel.send("Make sure you put an integer after the -d flag.")
            return

        weather_name = None
        if "-w " in command.split("\n")[0]:
            weather_name = command.split("\n")[0].split("-w ")[1].split("-")[0].strip()
        elif "--weather " in command.split("\n")[0]: 
            weather_name = command.split("\n")[0].split("--weather ")[1].split("-")[0].strip()

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
            if day is not None:
                game.teams['away'].set_pitcher(rotation_slot = day)
                game.teams['home'].set_pitcher(rotation_slot = day)
            channel = msg.channel
            
            if weather_name is not None and weather_name in weather.all_weathers().keys():
                game.weather = weather.all_weathers()[weather_name](game)
                

            game_task = asyncio.create_task(watch_game(channel, game, user=msg.author, league=league))
            await game_task
        else:
            await msg.channel.send("We can't find one or both of those teams. Check your staging, chief.")
            return

class StartRandomGameCommand(Command):
    name = "randomgame"
    template = "m;randomgame"
    description = "Starts a 9-inning game between 2 entirely random teams. Embrace chaos!"

    async def execute(self, msg, command):
        if config()["game_freeze"]:
            await msg.channel.send("Patch incoming. We're not allowing new games right now.")
            return

        channel = msg.channel
        await channel.send("Rolling the bones... This might take a while.")
        teamslist = games.get_all_teams()

        game = games.game(random.choice(teamslist).finalize(), random.choice(teamslist).finalize())

        game_task = asyncio.create_task(watch_game(channel, game, user="the winds of chaos"))
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
    template = """m;saveteam
   [name] 
   [slogan] 
   [lineup]
   [rotation]"""

    description = """Saves a team to the database allowing it to be used for games. Send this command at the top of a list, with entries separated by new lines (shift+enter in discord, or copy+paste from notepad).
  - the first line of the list is your team's name.
  - the second line is the team's icon and slogan, generally this is an emoji followed by a space, followed by a short slogan.
  - the third line must be blank.
  - the next lines are your batters' names in the order you want them to appear in your lineup, lineups can contain any number of batters between 1 and 12.
  - there must be another blank line between your batters and your pitchers.
  - the final lines are the names of the pitchers in your rotation, rotations can contain any number of pitchers between 1 and 8.
If you did it correctly, you'll get a team embed with a prompt to confirm. hit the 👍 and your team will be saved!"""

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
    description = "Imports an onomancer collection as a new team. You can use the new onomancer simsim setting to ensure compatibility. Similarly to saveteam, you'll get a team embed with a prompt to confirm, hit the 👍 and your team will be saved!"

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
    description = "Shows the lineup, rotation, and slogan of any saved team in a discord embed with primary stat star ratings for all of the players. This command has fuzzy search so you don't need to type the full name of the team as long as you give enough to identify the team you're looking for."
    
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
    description = "Swaps a player from your lineup to the end of your rotation or your rotation to the end of your lineup. Requires team ownership and exact spelling of team name."

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
    description = "Moves a player within your lineup or rotation. If you want to instead move a player from your rotation to your lineup or vice versa, use m;swapsection instead. Requires team ownership and exact spelling of team name."

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
            else:
                if team.find_player(player_name)[2] is None or len(team.find_player(player_name)[2]) <= new_pos:
                    await msg.channel.send("You either gave us a number that was bigger than your current roster, or we couldn't find the player on the team. Try again.")
                    return

                if "batter" in command.split("\n")[0].lower():
                    roster = team.lineup
                elif "pitcher" in command.split("\n")[0].lower():
                    roster = team.rotation
                else:
                    roster = None

                if (roster is not None and team.slide_player_spec(player_name, new_pos, roster)) or (roster is None and team.slide_player(player_name, new_pos)):
                    await msg.channel.send(embed=build_team_embed(team))
                    games.update_team(team)
                    await msg.channel.send("Paperwork signed, stamped, copied, and faxed up to the goddess. Xie's pretty quick with this stuff.")
                else:
                    await msg.channel.send("You either gave us a number that was bigger than your current roster, or we couldn't find the player on the team. Try again.")
                    return

        except IndexError:
            await msg.channel.send("Four lines, remember? Command, then team, then name, and finally, new spot on the lineup or rotation.")

class AddPlayerCommand(Command):
    name = "addplayer"
    template = """m;addplayer pitcher (or m;addplayer batter)
    [team name]
    [player name]"""
    description = "Adds a new player to the end of your team, either in the lineup or the rotation depending on which version you use. Requires team ownership and exact spelling of team name."

    async def execute(self, msg, command):
        try:
            team_name = command.split("\n")[1].strip()
            player_name = command.split("\n")[2].strip()
            team, owner_id = games.get_team_and_owner(team_name)
            if owner_id != msg.author.id and msg.author.id not in config()["owners"]:
                await msg.channel.send("You're not authorized to mess with this team. Sorry, boss.")
                return

            new_player = games.player(ono.get_stats(player_name))

            if "batter" in command.split("\n")[0].lower():
                if not team.add_lineup(new_player)[0]:
                    await msg.channel.send("Too many batters 🎶")
                    return
            elif "pitcher" in command.split("\n")[0].lower():
                if not team.add_pitcher(new_player):
                    await msg.channel.send("8 pitchers is quite enough, we think.")
                    return
            else:
                await msg.channel.send("You have to tell us if you want a pitcher or a batter, boss. Just say so in the first line, with the command.")
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
    description = "Removes a player from your team. If there are multiple copies of the same player on a team this will only delete the first one. Requires team ownership and exact spelling of team name."

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

class ReplacePlayerCommand(Command):
    name = "replaceplayer"
    template = """m;replaceplayer
    [team name]
    [player name to **remove**]
    [player name to **add**]"""
    description = "Replaces a player on your team. If there are multiple copies of the same player on a team this will only replace the first one. Requires team ownership and exact spelling of team name."

    async def execute(self, msg, command):
        try:
            team_name = command.split("\n")[1].strip()
            remove_name = command.split("\n")[2].strip()
            add_name = command.split("\n")[3].strip()
            team, owner_id = games.get_team_and_owner(team_name)
            if owner_id != msg.author.id and msg.author.id not in config()["owners"]:
                await msg.channel.send("You're not authorized to mess with this team. Sorry, boss.")
                return

            old_player, old_pos, old_list = team.find_player(remove_name)
            new_player = games.player(ono.get_stats(add_name))

            if old_player is None:
                await msg.channel.send("We've got bad news: that player isn't on your team. The good news is that... that player isn't on your team?")
                return

            else:
                if old_list == team.lineup:
                    team.delete_player(remove_name)
                    team.add_lineup(new_player)
                    team.slide_player(add_name, old_pos+1)
                else:
                    team.delete_player(remove_name)
                    team.add_pitcher(new_player)
                    team.slide_player(add_name, old_pos+1)
                await msg.channel.send(embed=build_team_embed(team))
                games.update_team(team)
                await msg.channel.send("Paperwork signed, stamped, copied, and faxed up to the goddess. Xie's pretty quick with this stuff.")
        except IndexError:
            await msg.channel.send("Four lines, remember? Command, then team, then the two names.")

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
    description = "Allows you to delete the team with the provided name. You'll get an embed with a confirmation to prevent accidental deletions. Hit the 👍 and your team will be deleted.. Requires team ownership. If you are the owner and the bot is telling you it's not yours, contact xvi and xie can assist."

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
        if self.isauthorized(msg.author):
            new_owner = msg.mentions[0]
            team_name = command.strip().split("> ",1)[1]
            if db.assign_owner(team_name, new_owner.id):
                await msg.channel.send(f"{team_name} is now owned by {new_owner.display_name}. Don't break it.")
            else:
                await msg.channel.send("We couldn't find that team. Typo?")

class StartTournamentCommand(Command):
    name = "starttournament"
    template = """m;starttournament
    [tournament name]
    [list of teams, each on a new line]"""
    description = "Starts a randomly seeded tournament with the provided teams, automatically adding byes as necessary. All series have a 5 minute break between games and by default there is a 10 minute break between rounds. The current tournament format is:\nBest of 5 until the finals, which are Best of 7."

    async def execute(self, msg, command):
        if config()["game_freeze"]:
            await msg.channel.send("Patch incoming. We're not allowing new games right now.")
            return

        to_parse = command.split("\n")[0]

        if "--rounddelay " in to_parse:
            try:
                round_delay = int(to_parse.split("--rounddelay ")[1].split("-")[0].strip())
            except ValueError:
                await msg.channel.send("The delay between rounds should be a whole number.")
                return
            if round_delay < 1 or round_delay > 120:
                await msg.channel.send("The delay between rounds has to  bebetween 1 and 120 minutes.")
                return
        else:
            round_delay = 10
       
        if "--bestof " in command.split("\n")[0]:
            try:
                series_length = int(to_parse.split("--bestof ")[1].split("-")[0].strip())
                if series_length % 2 == 0 or series_length < 0:
                    raise ValueError
            except ValueError:
                await msg.channel.send("Series length has to be an odd positive integer.")
                return
            if msg.author.id not in config()["owners"] and series_length > 21:
                await msg.channel.send("That's too long, boss. We have to run patches *some* time.")
                return
        else:
            series_length = 5

        if "--finalsbestof " in command.split("\n")[0]:
            try:
                finals_series_length = int(to_parse.split("--finalsbestof ")[1].split("-")[0].strip())
                if finals_series_length % 2 == 0 or finals_series_length < 0:
                    raise ValueError
            except ValueError:
                await msg.channel.send("Finals series length has to be an odd positive integer.")
                return
            if msg.author.id not in config()["owners"] and finals_series_length > 21:
                await msg.channel.send("That's too long, boss. We have to run patches *some* time.")
                return
        else:
            finals_series_length = 7

        rand_seed = not "--seeding stars" in command.split("\n")[0]

        
        

        tourney_name = command.split("\n")[1]
        list_of_team_names = command.split("\n")[2:]
        team_dic = {}
        for name in list_of_team_names:
            team = get_team_fuzzy_search(name.strip())
            if team == None:
                await msg.channel.send(f"We couldn't find {name}. Try again?")
                return
            add = True
            for extant_team in team_dic.keys():
                if extant_team.name == team.name:
                    add = False
            if add:
                team_dic[team] = {"wins": 0}

        channel = msg.channel
        await msg.delete()

        if len(team_dic) < 2:
            await msg.channel.send("One team does not a tournament make.")
            return

        id = random.randint(1111,9999)

        tourney = leagues.tournament(tourney_name, team_dic, series_length = series_length, finals_series_length = finals_series_length,  id=id, secs_between_rounds = round_delay * 60)
        tourney.build_bracket(random_sort = rand_seed)

        
        await start_tournament_round(channel, tourney)


class DraftPlayerCommand(Command):
    name = "draft"
    template = "m;draft [playername]"
    description = "On your turn during a draft, use this command to pick your player."

    async def execute(self, msg, command):
        """
        This is a no-op definition. `StartDraftCommand` handles the orchestration directly,
        this is just here to provide a help entry and so the command dispatcher recognizes it
        as valid.
        """
        pass


class StartDraftCommand(Command):
    name = "startdraft"
    template = "m;startdraft\n[mention]\n[teamname]\n[slogan]"
    description = """Starts a draft with an arbitrary number of participants. Send this command at the top of the list with each mention, teamname, and slogan on their own lines (shift+enter in discord).
 - The draft will proceed in the order that participants were entered.
 - 20 players will be available for draft at a time, and the pool will refresh automatically when it becomes small.
 - Each participant will be asked to draft 12 hitters then finally one pitcher.
 - The draft will start only once every participant has given a 👍 to begin.
 - use the command `d`, `draft`, or `m;draft` on your turn to draft someone
    """

    async def execute(self, msg, command):
        draft = Draft.make_draft()
        mentions = {f'<@!{m.id}>' for m in msg.mentions}
        content = msg.content.split('\n')[1:]  # drop command out of message
        if not content or len(content) % 3:
            await msg.channel.send('Invalid list')
            raise ValueError('Invalid length')

        for i in range(0, len(content), 3):
            handle_token = content[i].strip()
            for mention in mentions:
                if mention in handle_token:
                    handle = mention
                    break
            else:
                await msg.channel.send(f"I don't recognize {handle_token}")
                return
            team_name = content[i + 1].strip()
            if games.get_team(team_name):
                await msg.channel.send(f'Sorry {handle}, {team_name} already exists')
                return
            slogan = content[i + 2].strip()
            draft.add_participant(handle, team_name, slogan)

        success = await self.wait_start(msg.channel, mentions)
        if not success:
            return

        draft.start_draft()
        footer = f"The draft class of {random.randint(2007, 2075)}"
        while draft.round <= DRAFT_ROUNDS:
            message_prefix = f'Round {draft.round}/{DRAFT_ROUNDS}:'
            if draft.round == DRAFT_ROUNDS:
                body = random.choice([
                    f"Now just choose a pitcher and we can finish off this paperwork for you, {draft.active_drafter}",
                    f"Pick a pitcher, {draft.active_drafter}, and we can all go home happy. 'Cept your players. They'll have to play baseball.",
                    f"Almost done, {draft.active_drafter}. Pick your pitcher.",
                ])
                message = f"⚾️ {message_prefix} {body}"
            else:
                body = random.choice([
                    f"Choose a batter, {draft.active_drafter}",
                    f"{draft.active_drafter}, your turn. Pick one.",
                    f"Pick one to fill your next lineup slot, {draft.active_drafter}",
                    f"Alright, {draft.active_drafter}, choose a batter.",
                ])
                message = f"🏏 {message_prefix} {body}"
            await msg.channel.send(
                message,
                embed=build_draft_embed(draft.get_draftees(), footer=footer),
            )
            try:
                draft_message = await self.wait_draft(msg.channel, draft)
                draft.draft_player(f'<@!{draft_message.author.id}>', draft_message.content.split(' ', 1)[1])
            except SlowDraftError:
                player = random.choice(draft.get_draftees())
                await msg.channel.send(f"I'm not waiting forever. You get {player}. Next.")
                draft.draft_player(draft.active_drafter, player)
            except ValueError as e:
                await msg.channel.send(str(e))
            except IndexError:
                await msg.channel.send("Quit the funny business.")

        for handle, team in draft.get_teams():
            await msg.channel.send(
                random.choice([
                    f"Done and dusted, {handle}. Here's your squad.",
                    f"Behold the {team.name}, {handle}. Flawless, we think.",
                    f"Oh, huh. Interesting stat distribution. Good luck, {handle}.",
                ]),
                embed=build_team_embed(team),
            )
        try:
            draft.finish_draft()
        except Exception as e:
            await msg.channel.send(str(e))

    async def wait_start(self, channel, mentions):
        start_msg = await channel.send("Sound off, folks. 👍 if you're good to go " + " ".join(mentions))
        await start_msg.add_reaction("👍")
        await start_msg.add_reaction("👎")

        def react_check(react, user):
            return f'<@!{user.id}>' in mentions and react.message == start_msg

        while True:
            try:
                react, _ = await client.wait_for('reaction_add', timeout=60.0, check=react_check)
                if react.emoji == "👎":
                    await channel.send("We dragged out the photocopier for this! Fine, putting it back.")
                    return False
                if react.emoji == "👍":
                    reactors = set()
                    async for user in react.users():
                        reactors.add(f'<@!{user.id}>')
                    if reactors.intersection(mentions) == mentions:
                        return True
            except asyncio.TimeoutError:
                await channel.send("Y'all aren't ready.")
                return False
        return False

    async def wait_draft(self, channel, draft):

        def check(m):
            if m.channel != channel:
                return False
            if m.content.startswith('d ') or m.content.startswith('draft '):
                return True
            for prefix in config()['prefix']:
                if m.content.startswith(prefix + 'draft '):
                    return True
            return False

        try:
            draft_message = await client.wait_for('message', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            raise SlowDraftError('Too slow')
        return draft_message

            
class StartLeagueCommand(Command):
    name = "startleague"
    template = "m;startleague [league name]\n[games per hour]"
    description = """Optional flags for the first line: `--queue X` or `-q X` to play X number of series before stopping; `--noautopostseason` will pause the league before starting postseason.
Starts games from a league with a given name, provided that league has been saved on the website and has been claimed using claimleague. The games per hour sets how often the games will start (e.g. GPH 2 will start games at X:00 and X:30). By default it will play the entire season followed by the postseason and then stop but this can be customized using the flags.
Not every team will play every series, due to how the scheduling algorithm is coded but it will all even out by the end."""

    async def execute(self, msg, command):
        if config()["game_freeze"]:
            await msg.channel.send("Patch incoming. We're not allowing new games right now.")
            return

        league_name = command.split("-")[0].split("\n")[0].strip()
        autoplay = None

        
        try:          
            if "--queue " in command:
                autoplay = int(command.split("--queue ")[1].split("\n")[0])
            elif "-q " in command:
                autoplay = int(command.split("-q ")[1].split("\n")[0])
            if autoplay is not None and autoplay <= 0:
                raise ValueError
            elif autoplay is None:
                autoplay = -1
        except ValueError:
            await msg.channel.send("Sorry boss, the queue flag needs a natural number. Any whole number over 0 will do just fine.")
            return
        except IndexError:
            await msg.channel.send("We need a games per hour number in the second line.")
            return

        

        try:
            gph = int(command.split("\n")[1].strip())
            if gph < 1 or gph > 12:
                raise ValueError
        except ValueError:
            await msg.channel.send("Chief, we need a games per hour number between 1 and 12. We think that's reasonable.")
            return
        except IndexError:
            await msg.channel.send("We need a games per hour number in the second line.")
            return

        if league_exists(league_name):
            league = leagues.load_league_file(league_name)
            if "--noautopostseason" in command:
                await msg.channel.send("Automatic postseason disabled.")
                autoplay = int(list(league.schedule.keys())[-1]) - league.day_to_series_num(league.day) + 1

            if league.historic:
                await msg.channel.send("That league is done and dusted, chief. Sorry.")
                return
            for active_league in active_leagues:
                if active_league.name == league.name:
                    await msg.channel.send("That league is already running, boss. Patience is a virtue, you know.")
                    return
            if (league.owner is not None and msg.author.id in league.owner) or msg.author.id in config()["owners"] or league.owner is None:
                league.autoplay = autoplay
                league.games_per_hour = gph
                if str(league.day_to_series_num(league.day)) not in league.schedule.keys():
                    await league_postseason(msg.channel, league)
                elif league.day % league.series_length == 1:
                    await start_league_day(msg.channel, league)
                else:
                    await start_league_day(msg.channel, league, partial = True)
            else:
                await msg.channel.send("You don't have permission to manage that league.")
                return
        else:
            await msg.channel.send("Couldn't find that league, boss. Did you save it on the website?")

class LeagueDisplayCommand(Command):
    name = "leaguestandings"
    template = "m;leaguestandings [league name]"
    description = "Displays the current standings for the given league. Use `--season X` or `-s X` to get standings from season X of that league."

    async def execute(self, msg, command):
        if league_exists(command.split("-")[0].strip()):
            league = leagues.load_league_file(command.split("-")[0].strip())

            try:
                if "--season " in command:
                    season_num = int(command.split("--season ")[1])
                    await msg.channel.send(embed=league.past_standings(season_num))
                elif "-s " in command:
                    season_num = int(command.split("-s ")[1])
                    await msg.channel.send(embed=league.past_standings(season_num))
                else:
                    await msg.channel.send(embed=league.standings_embed())
            except ValueError:
                await msg.channel.send("Give us a proper number, boss.")
            except TypeError:
                await msg.channel.send("That season hasn't been played yet, chief.")
        else:
            await msg.channel.send("Can't find that league, boss.")

class LeagueLeadersCommand(Command):
    name = "leagueleaders"
    template = "m;leagueleaders [league name]\n[stat name/abbreviation]"
    description = "Displays a league's leaders in the given stat. A list of the allowed stats can be found on the github readme."

    async def execute(self, msg, command):
        if league_exists(command.split("\n")[0].strip()):
            league = leagues.load_league_file(command.split("\n")[0].strip())
            stat_name = command.split("\n")[1].strip()
            try:
                stat_embed = league.stat_embed(stat_name)
            except IndexError:
                await msg.channel.send("Nobody's played enough games to get meaningful stats in that category yet, chief. Try again after the next game or two.")
                return

            if stat_embed is None:
                await msg.channel.send("We don't know what that stat is, chief.")
                return
            try:
                await msg.channel.send(embed=stat_embed)
                return
            except:
                await msg.channel.send("Nobody's played enough games to get meaningful stats in that category yet, chief. Try again after the next game or two.")
                return

        await msg.channel.send("Can't find that league, boss.")

class LeagueDivisionDisplayCommand(Command):
    name = "divisionstandings"
    template = "m;divisionstandings [league name]\n[division name]"
    description = "Displays the current standings for the given division in the given league."

    async def execute(self, msg, command):
        if league_exists(command.split("\n")[0].strip()):
            league = leagues.load_league_file(command.split("\n")[0].strip())
            division_name = command.split("\n")[1].strip()
            division = None
            for subleague in iter(league.league.keys()):
                for div in iter(league.league[subleague].keys()):
                    if div == division_name:
                        division = league.league[subleague][div]
            if division is None:
                await msg.channel.send("Chief, that division doesn't exist in that league.")
                return

            try:
                await msg.channel.send(embed=league.standings_embed_div(division, division_name))
            except ValueError:
                await msg.channel.send("Give us a proper number, boss.")
            #except TypeError:
                #await msg.channel.send("That season hasn't been played yet, chief.")
        else:
            await msg.channel.send("Can't find that league, boss.")

class LeagueWildcardCommand(Command):
    name = "leaguewildcard"
    template = "m;leaguewildcard [league name]"
    description = "Displays the current wildcard race for the given league, if the league has wildcard slots."

    async def execute(self, msg, command):
        if league_exists(command.strip()):
            league = leagues.load_league_file(command.strip())
            if league.constraints["wild_cards"] > 0:
                await msg.channel.send(embed=league.wildcard_embed())
            else:
                await msg.channel.send("That league doesn't have wildcards, boss.")
        else:
            await msg.channel.send("Can't find that league, boss.")

class LeaguePauseCommand(Command):
    name = "pauseleague"
    template = "m;pauseleague [league name]"
    description = "Tells a currently running league to stop running after the current series."

    async def execute(self, msg, command):
        league_name = command.strip()
        for active_league in active_leagues:
            if active_league.name == league_name:
                if (active_league.owner is not None and msg.author.id in active_league.owner) or msg.author.id in config()["owners"]:
                    active_league.autoplay = 0
                    await msg.channel.send(f"Loud and clear, chief. {league_name} will stop after this series is over.")
                    return
                else:
                    await msg.channel.send("You don't have permission to manage that league.")
                    return
        await msg.channel.send("That league either doesn't exist or isn't running.")

class LeagueClaimCommand(Command):
    name = "claimleague"
    template = "m;claimleague [league name]"
    description = "Claims an unclaimed league. Do this as soon as possible after creating the league, or it will remain unclaimed."

    async def execute(self, msg, command):
        league_name = command.strip()
        if league_exists(league_name):
            league = leagues.load_league_file(league_name)
            if league.owner is None:
                league.owner = [msg.author.id]
                leagues.save_league(league)
                await msg.channel.send(f"The {league.name} commissioner is doing a great job. That's you, by the way.")
                return
            else:
                await msg.channel.send("That league has already been claimed!")
        else:
            await msg.channel.send("Can't find that league, boss.")

class LeagueAddOwnersCommand(Command):
    name = "addleagueowner"
    template = "m;addleagueowner [league name]\n[user mentions]"
    description = "Adds additional owners to a league."

    async def execute(self, msg, command):
        league_name = command.split("\n")[0].strip()
        if league_exists(league_name):
            league = leagues.load_league_file(league_name)
            if (league.owner is not None and msg.author.id in league.owner) or (league.owner is not None and msg.author.id in config()["owners"]):
                for user in msg.mentions:
                    if user.id not in league.owner:
                        league.owner.append(user.id)
                leagues.save_league(league)
                await msg.channel.send(f"The new {league.name} front office is now up and running.")
                return
            else:
                await msg.channel.send(f"That league isn't yours, boss.")
                return
        else:
            await msg.channel.send("Can't find that league, boss.")
            
class LeagueScheduleCommand(Command):
    name = "leagueschedule"
    template = "m;leagueschedule [league name]"
    description = "Sends an embed with the given league's schedule for the next 4 series."

    async def execute(self, msg, command):
        league_name = command.split("\n")[0].strip()
        if league_exists(league_name):
            league = leagues.load_league_file(league_name)
            current_series = league.day_to_series_num(league.day)
            if str(current_series+1) in league.schedule.keys():
                sched_embed = discord.Embed(title=f"{league.name}'s Schedule:", color=discord.Color.magenta())
                days = [0,1,2,3]
                for day in days:
                    if str(current_series+day) in league.schedule.keys():
                        schedule_text = ""
                        teams = league.team_names_in_league()
                        for game in league.schedule[str(current_series+day)]:
                            schedule_text += f"**{game[0]}** @ **{game[1]}**\n"
                            teams.pop(teams.index(game[0]))
                            teams.pop(teams.index(game[1]))
                        if len(teams) > 0:
                            schedule_text += "Resting:\n"
                            for team in teams:
                                schedule_text += f"**{team}**\n"
                        sched_embed.add_field(name=f"Days {((current_series+day-1)*league.series_length) + 1} - {(current_series+day)*(league.series_length)}", value=schedule_text, inline = False)
                await msg.channel.send(embed=sched_embed)
            else:
                await msg.channel.send("That league's already finished with this season, boss.")
        else:
            await msg.channel.send("We can't find that league. Typo?")

class LeagueTeamScheduleCommand(Command):
    name = "teamschedule"
    template = "m;teamschedule [league name]\n[team name]"
    description = "Sends an embed with the given team's schedule in the given league for the next 7 series."

    async def execute(self, msg, command):
        league_name = command.split("\n")[0].strip()
        team_name = command.split("\n")[1].strip()
        team = get_team_fuzzy_search(team_name)
        if league_exists(league_name):
            league = leagues.load_league_file(league_name)
            current_series = league.day_to_series_num(league.day)

            if team.name not in league.team_names_in_league():
                await msg.channel.send("Can't find that team in that league, chief.")
                return

            if str(current_series+1) in league.schedule.keys():
                sched_embed = discord.Embed(title=f"{team.name}'s Schedule for the {league.name}:", color=discord.Color.purple())
                days = [0,1,2,3,4,5,6]
                for day in days:
                    if str(current_series+day) in league.schedule.keys():
                        schedule_text = ""
                        for game in league.schedule[str(current_series+day)]:
                            if team.name in game:
                                schedule_text += f"**{game[0]}** @ **{game[1]}**"
                        if schedule_text == "":
                            schedule_text += "Resting"
                        sched_embed.add_field(name=f"Days {((current_series+day-1)*league.series_length) + 1} - {(current_series+day)*(league.series_length)}", value=schedule_text, inline = False)
                await msg.channel.send(embed=sched_embed)
            else:
                await msg.channel.send("That league's already finished with this season, boss.")
        else:
            await msg.channel.send("We can't find that league. Typo?")
            
class LeagueRegenerateScheduleCommand(Command):
    name = "leagueseasonreset"
    template = "m;leagueseasonreset [league name]"
    description = "Completely scraps the given league's current season, resetting everything to day 1 of the current season. Requires ownership."

    async def execute(self, msg, command):
        league_name = command.split("\n")[0].strip()
        if league_exists(league_name):
            league = leagues.load_league_file(league_name)
            if (league.owner is not None and msg.author.id in league.owner) or (league.owner is not None and msg.author.id in config()["owners"]):
                await msg.channel.send("You got it, boss. Give us two seconds and a bucket of white-out.")
                season_restart(league)
                league.season -= 1
                league.season_reset()               
                await asyncio.sleep(1)
                await msg.channel.send("Done and dusted. Go ahead and start the league again whenever you want.")
                return
            else:
                await msg.channel.send("That league isn't yours, boss.")
                return
        else:
            await msg.channel.send("We can't find that league. Typo?")

class LeagueForceStopCommand(Command):
    name = "leagueforcestop"
    template = "m;leagueforcestop [league name]"
    description = "Halts a league and removes it from the list of currently running leagues. To be used in the case of crashed loops."

    def isauthorized(self, user):
        return user.id in config()["owners"]

    async def execute(self, msg, command):
        league_name = command.split("\n")[0].strip()
        for index in range(0,len(active_leagues)):
            if active_leagues[index].name == league_name:
                active_leagues.pop(index)
                await msg.channel.send("League halted, boss. We hope you did that on purpose.")
                return
        await msg.channel.send("That league either doesn't exist or isn't in the active list. So, huzzah?")

class LeagueSwapTeamCommand(Command):
    name = "leagueswapteam"
    template = "m;leagueswapteam [league name]\n[team to remove]\n[team to add]"
    description = "Adds a team to a league, removing the old one in the process. Can only be executed by a league owner, and only before the start of a new season."
         
    async def execute(self, msg, command):
        league_name = command.split("\n")[0].strip()
        if league_exists(league_name):
            league = leagues.load_league_file(league_name)
            if league.day != 1:
                await msg.channel.send("That league hasn't finished its current season yet, chief. Either reset it, or be patient.")
                return
            if (league.owner is not None and msg.author.id in league.owner) or (league.owner is not None and msg.author.id in config()["owners"]):
                try:
                    team_del = get_team_fuzzy_search(command.split("\n")[1].strip())
                    team_add = get_team_fuzzy_search(command.split("\n")[2].strip())
                except IndexError:
                    await msg.channel.send("Three lines, boss. Make sure you give us the team to remove, then the team to add.")
                    return
                if team_add.name == team_del.name:
                    await msg.channel.send("Quit being cheeky. The teams have to be different.")
                    return

                if team_del is None or team_add is None:
                    await msg.channel.send("We couldn't find one or both of those teams, boss. Try again.")
                    return
                subleague, division = league.find_team(team_del)               

                if subleague is None or division is None:
                    await msg.channel.send("That first team isn't in that league, chief. So, that's good, right?")
                    return

                if league.find_team(team_add)[0] is not None:
                    await msg.channel.send("That second team is already in that league, chief. No doubles.")
                    return

                for index in range(0, len(league.league[subleague][division])):
                    if league.league[subleague][division][index].name == team_del.name:
                        league.league[subleague][division].pop(index)
                        league.league[subleague][division].append(team_add)
                league.schedule = {}
                league.generate_schedule()
                leagues.save_league_as_new(league)
                await msg.channel.send(embed=league.standings_embed())
                await msg.channel.send("Paperwork signed, stamped, copied, and faxed up to the goddess. Xie's pretty quick with this stuff.")
            else:
                await msg.channel.send("That league isn't yours, chief.")
        else:
            await msg.channel.send("We can't find that league.")

class LeagueRenameCommand(Command):
    name = "leaguerename"
    template = "m;leaguerename [league name]\n[old subleague/division name]\n[new subleague/division name]"
    description = "Changes the name of an existing subleague or division. Can only be executed by a league owner, and only before the start of a new season."
         
    async def execute(self, msg, command):
        league_name = command.split("\n")[0].strip()
        if league_exists(league_name):
            league = leagues.load_league_file(league_name)
            if league.day != 1:
                await msg.channel.send("That league hasn't finished its current season yet, chief. Either reset it, or be patient.")
                return
            if (league.owner is not None and msg.author.id in league.owner) or (league.owner is not None and msg.author.id in config()["owners"]):
                try:
                    old_name = command.split("\n")[1].strip()
                    new_name = command.split("\n")[2].strip()
                except IndexError:
                    await msg.channel.send("Three lines, boss. Make sure you give us the old name, then the new name, on their own lines.")
                    return

                if old_name == new_name:
                    await msg.channel.send("Quit being cheeky. They have to be different names, clearly.")


                found = False
                for subleague in league.league.keys():
                    if subleague == new_name:
                        found = True
                        break
                    for division in league.league[subleague]:
                        if division == new_name:
                            found = True
                            break
                if found:
                    await msg.channel.send(f"{new_name} is already present in that league, chief. They have to be different.")

                found = False
                for subleague in league.league.keys():
                    if subleague == old_name:
                        league.league[new_name] = league.league.pop(old_name)
                        found = True
                        break
                    for division in league.league[subleague]:
                        if division == old_name:
                            league.league[subleague][new_name] = league.league[subleague].pop(old_name)
                            found = True
                            break
                if not found:
                    await msg.channel.send(f"We couldn't find {old_name} anywhere in that league, boss.")
                    return
                leagues.save_league_as_new(league)
                await msg.channel.send(embed=league.standings_embed())
                await msg.channel.send("Paperwork signed, stamped, copied, and faxed up to the goddess. Xie's pretty quick with this stuff.")
            else:
                await msg.channel.send("That league isn't yours, chief.")
        else:
            await msg.channel.send("We can't find that league.")

class OBLExplainCommand(Command):
    name = "oblhelp"
    template = "m;oblhelp"
    description = "Explains the One Big League!"

    async def execute(self, msg, command):
        await msg.channel.send("""The One Big League, or OBL, is an asynchronous league that includes every team in the simsim's database. To participate, just use the m;oblteam command with your team of choice. **No signup is required!** This will give you a list of five opponents; playing against one of them and winning nets you a point, and will refresh the list with five new opponents. **Losing results in no penalty!** Each meta-season will last for a few weeks, after which the leaderboards are reset to start the race again!

Look out for the people wrestling emoji, which indicates the potential for a :people_wrestling:Wrassle Match:people_wrestling:, where both teams are on each others' lists and both have the opportunity to score a point. Team rankings and points can also be viewed in the m;oblteam command, and the overall OBL leaderboard can be checked with the m;oblstandings command. Best of luck!!
""")

class OBLLeaderboardCommand(Command):
    name = "oblstandings"
    template = "m;oblstandings"
    description = "Displays the 15 teams with the most OBL points in this meta-season."
         
    async def execute(self, msg, command):
        leaders_list = db.obl_leaderboards()[:15]
        leaders = []
        rank = 1
        for team, points in leaders_list:
            leaders.append({"name" : team, "points" : points})
            rank += 1

        embed = discord.Embed(color=discord.Color.red(), title="The One Big League")
        for index in range(0, len(leaders)):
            embed.add_field(name=f"{index+1}. {leaders[index]['name']}", value=f"{leaders[index]['points']} points" , inline = False)
        await msg.channel.send(embed=embed)

class OBLTeamCommand(Command):
    name = "oblteam"
    template = "m;oblteam [team name]"
    description = "Displays a team's rank, current OBL points, and current opponent selection."

    async def execute(self, msg, command):
        team = get_team_fuzzy_search(command.strip())
        if team is None:
            await msg.channel.send("Sorry boss, we can't find that team.")
            return

        rival_team = None
        points, beaten_teams_list, opponents_string, rank, rival_name = db.get_obl_stats(team, full=True)
        opponents_list = db.newline_string_to_list(opponents_string)
        for index in range(0, len(opponents_list)):
            oppteam = get_team_fuzzy_search(opponents_list[index])
            opplist = db.get_obl_stats(oppteam)[1]
            if team.name in opplist:
                opponents_list[index] = opponents_list[index] + " 🤼"
            if rival_name == opponents_list[index]:
                opponents_list[index] = opponents_list[index] + " 😈"
        if rival_name is not None:
            rival_team = games.get_team(rival_name)
        opponents_string = db.list_to_newline_string(opponents_list)

        embed = discord.Embed(color=discord.Color.red(), title=f"{team.name} in the One Big League")
        embed.add_field(name="OBL Points", value=points)
        embed.add_field(name="Rank", value=rank)
        embed.add_field(name="Bounty Board", value=opponents_string, inline=False)
        if rival_team is not None:
            r_points, r_beaten_teams_list, r_opponents_string, r_rank, r_rival_name = db.get_obl_stats(rival_team, full=True)
            embed.add_field(name="Rival", value=f"**{rival_team.name}**: Rank {r_rank}\n{rival_team.slogan}\nPoints: {r_points}")
            if r_rival_name == team.name:
                embed.set_footer(text="🔥")
        else:
            embed.set_footer(text="Set a rival with m;oblrival!")
        await msg.channel.send(embed=embed)

class OBLSetRivalCommand(Command):
    name = "oblrival"
    template = "m;oblrival\n[your team name]\n[rival team name]"
    description = "Sets your team's OBL rival. Can be changed at any time. Requires ownership."

    async def execute(self, msg, command):
        try:
            team_i = get_team_fuzzy_search(command.split("\n")[1].strip())
            team_r = get_team_fuzzy_search(command.split("\n")[2].strip())
        except IndexError:
            await msg.channel.send("You didn't give us enough lines. Command on the top, your team in the middle, and your rival at the bottom.")
            return
        team, owner_id = games.get_team_and_owner(team_i.name)
        if team is None or team_r is None:
            await msg.channel.send("Can't find one of those teams, boss. Typo?")
            return
        elif owner_id != msg.author.id and msg.author.id not in config()["owners"]:
            await msg.channel.send("You're not authorized to mess with this team. Sorry, boss.")
            return
        try:
            db.set_obl_rival(team, team_r)
            await msg.channel.send("One pair of mortal enemies, coming right up. Unless you're more of the 'enemies to lovers' type. We can manage that too, don't worry.")
        except:
            await msg.channel.send("Hm. We don't think that team has tried to do anything in the One Big League yet, so you'll have to wait for consent. Get them to check their bounty board.")

class OBLConqueredCommand(Command):
    name = "oblwins"
    template = "m;oblwins [team name]"
    description = "Displays all teams that a given team has won points off of."

    async def execute(self, msg, command):
        team = get_team_fuzzy_search(command.strip())
        if team is None:
            await msg.channel.send("Sorry boss, we can't find that team.")
            return

        points, teams, oppTeams, rank, rivalName = db.get_obl_stats(team, full=True)
        pages = []
        page_max = math.ceil(len(teams)/25)

        title_text = f"Rank {rank}: {team.name}"

        for page in range(0,page_max):
            embed = discord.Embed(color=discord.Color.red(), title=title_text)
            embed.set_footer(text = f"{points} OBL Points")
            for i in range(0,25):             
                try:
                    thisteam = games.get_team(teams[i+25*page])
                    if thisteam.slogan.strip() != "":
                        embed.add_field(name=thisteam.name, value=thisteam.slogan)
                    else:
                        embed.add_field(name=thisteam.name, value="404: Slogan not found")
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
    ReplacePlayerCommand(),
    DeleteTeamCommand(),
    ShowTeamCommand(),
    ShowAllTeamsCommand(),
    SearchTeamsCommand(),
    StartGameCommand(),
    StartRandomGameCommand(),
    StartTournamentCommand(),
    OBLExplainCommand(),
    OBLTeamCommand(),
    OBLSetRivalCommand(),
    OBLConqueredCommand(),
    OBLLeaderboardCommand(),
    LeagueClaimCommand(),
    LeagueAddOwnersCommand(),
    StartLeagueCommand(),
    LeaguePauseCommand(),
    LeagueDisplayCommand(),
    LeagueLeadersCommand(),
    LeagueDivisionDisplayCommand(),
    LeagueWildcardCommand(),
    LeagueScheduleCommand(),
    LeagueTeamScheduleCommand(),
    LeagueRegenerateScheduleCommand(),
    LeagueSwapTeamCommand(),
    LeagueRenameCommand(),
    LeagueForceStopCommand(),
    CreditCommand(),
    RomanCommand(),
    HelpCommand(),
    StartDraftCommand(),
    DraftPlayerCommand()
]

watching = False
client = discord.Client()
gamesarray = []
active_tournaments = []
active_leagues = []
active_standings = {}
setupmessages = {}


thread1 = threading.Thread(target=main_controller.update_loop)
thread1.start()

def config():
    if not os.path.exists(os.path.dirname(config_filename)):
        os.makedirs(os.path.dirname(config_filename))
    if not os.path.exists(config_filename):
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
        with open(config_filename, "w") as config_file:
            json.dump(config_dic, config_file, indent=4)
            print("please fill in bot token and any bot admin discord ids to the new config.json file!")
            quit()
    else:
        with open(config_filename) as config_file:
            return json.load(config_file)

@client.event
async def on_ready():
    global watching
    db.initialcheck()
    print(f"logged in as {client.user} with token {config()['token']} to {len(client.guilds)} servers")
    if not watching:
        watching = True
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

    if msg.author == client.user or not msg.webhook_id is None:
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


    id = str(uuid4())
    ext = "?game="+id
    if league is not None:
        ext += "&league=" + urllib.parse.quote_plus(league)

    await channel.send(f"{newgame.teams['away'].name} vs. {newgame.teams['home'].name}, starting at {config()['simmadome_url']+ext}")
    gamesarray.append((newgame, channel, user, id))

    main_controller.master_games_dic[id] = (newgame, state_init, discrim_string)

def prepare_game(newgame, league = None, weather_name = None):
    if weather_name is None and newgame.weather.name == "Sunny":
        weathers = weather.all_weathers()
        newgame.weather = weathers[random.choice(list(weathers.keys()))](newgame)

    state_init = {
        "away_name" : newgame.teams['away'].name,
        "home_name" : newgame.teams['home'].name,
        "max_innings" : newgame.max_innings,
        "update_pause" : 0,
        "top_of_inning" : True,
        "victory_lap" : False,
        "weather_emoji" : newgame.weather.emoji,
        "weather_text" : newgame.weather.name,
        "start_delay" : 3,
        "end_delay" : 9
        } 

    if league is None:
        state_init["is_league"] = False
    else:
        state_init["is_league"] = True

    return newgame, state_init

async def start_tournament_round(channel, tourney, seeding = None):
    current_games = []
    if tourney.bracket is None:
        if seeding is None:
            tourney.build_bracket(random_sort=True)

    games_to_start = tourney.bracket.get_bottom_row()

    for pair in games_to_start:
        if pair[0] is not None and pair[1] is not None:
            team_a = get_team_fuzzy_search(pair[0].name)
            team_b = get_team_fuzzy_search(pair[1].name)

            if tourney.league is not None:
                if tourney.day is None:
                    tourney.day = tourney.league.day
                team_a.set_pitcher(rotation_slot = tourney.day)
                team_b.set_pitcher(rotation_slot = tourney.day)

            this_game = games.game(team_a.finalize(), team_b.finalize(), length = tourney.game_length)
            this_game, state_init = prepare_game(this_game)

            state_init["is_league"] = True

            if tourney.round_check():
                series_string = f"Best of {tourney.finals_length}:"
            else:
                series_string = f"Best of {tourney.series_length}:"
            state_init["title"] = f"{series_string} 0 - 0"
            discrim_string = tourney.name     

            id = str(uuid4())
            current_games.append((this_game, id))
            main_controller.master_games_dic[id] = (this_game, state_init, discrim_string)

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

        if tourney.league is not None:
            if tourney.day is None:
                tourney.day = tourney.league.day
            away_team.set_pitcher(rotation_slot = tourney.day)
            home_team.set_pitcher(rotation_slot = tourney.day)
            

        this_game = games.game(away_team.finalize(), home_team.finalize(), length = tourney.game_length)
        this_game, state_init = prepare_game(this_game)

        state_init["is_league"] = True

        if tourney.round_check():
            series_string = f"Best of {tourney.finals_length}:"
        else:
            series_string = f"Best of {tourney.series_length}:"

        state_init["title"] = f"{series_string} {wins_in_series[oldgame.teams['away'].name]} - {wins_in_series[oldgame.teams['home'].name]}"

        discrim_string = tourney.name     

        id = str(uuid4())
        games_list.append((this_game, id))
        main_controller.master_games_dic[id] = (this_game, state_init, discrim_string)

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
                    if game.over and ((key in main_controller.master_games_dic.keys() and main_controller.master_games_dic[key][1]["end_delay"] <= 8) or not key in main_controller.master_games_dic.keys()):
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
                        final_embed.add_field(name="Series score:", value=f"{wins_in_series[game.teams['away'].name]} - {wins_in_series[game.teams['home'].name]}")
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
        if tourney.league is not None:
            tourney.day += 1
        
        if len(queued_games) > 0:
            
            if tourney.league is not None:
                now = datetime.datetime.now()
                validminutes = [int((60 * div)/tourney.league.games_per_hour) for div in range(0,tourney.league.games_per_hour)]
                for i in range(0, len(validminutes)):
                    if now.minute > validminutes[i]:
                        if i <= len(validminutes)-3:
                            if validminutes[i+1] == now.minute:
                                delta = datetime.timedelta(minutes= (validminutes[i+2] - now.minute))
                            else:
                                delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
                        elif i <= len(validminutes)-2:
                            if validminutes[i+1] == now.minute:
                                delta = datetime.timedelta(minutes= (60 - now.minute))
                            else:
                                delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
                        else:
                            delta = datetime.timedelta(minutes= (60 - now.minute))           

                next_start = (now + delta).replace(second=0, microsecond=0)
                wait_seconds = (next_start - now).seconds
                await channel.send(f"The next batch of games for the {tourney.name} will start in {math.ceil(wait_seconds/60)} minutes.")
                await asyncio.sleep(wait_seconds)
            else:
                await channel.send(f"The next batch of games for {tourney.name} will start in {int(tourney.delay/60)} minutes.")
                await asyncio.sleep(tourney.delay)
            await channel.send(f"{len(queued_games)} games for {tourney.name}, starting at {filter_url}")
            games_list = await continue_tournament_series(tourney, queued_games, games_list, wins_in_series)
        else:
            tourney.active = False

    if finals: #if this last round was finals
        embed = discord.Embed(color = discord.Color.dark_purple(), title = f"{winner_list[0]} win the {tourney.name} finals!")
        if tourney.league is not None and tourney.day > tourney.league.day:
            tourney.league.day = tourney.day
        await channel.send(embed=embed)
        tourney.winner = get_team_fuzzy_search(winner_list[0])
        active_tournaments.pop(active_tournaments.index(tourney))
        return

    tourney.bracket.set_winners_dive(winner_list)

    winners_string = ""
    for game in tourney.bracket.get_bottom_row():
        winners_string += f"{game[0].name}\n{game[1].name}\n"

    if tourney.league is not None:
        now = datetime.datetime.now()
        validminutes = [int((60 * div)/tourney.league.games_per_hour) for div in range(0,tourney.league.games_per_hour)]
        for i in range(0, len(validminutes)):
            if now.minute > validminutes[i]:
                if i <= len(validminutes)-3:
                    if validminutes[i+1] == now.minute:
                        delta = datetime.timedelta(minutes= (validminutes[i+2] - now.minute))
                    else:
                        delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
                elif i <= len(validminutes)-2:
                    if validminutes[i+1] == now.minute:
                        delta = datetime.timedelta(minutes= (60 - now.minute))
                    else:
                        delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
                else:
                    delta = datetime.timedelta(minutes= (60 - now.minute))           

        next_start = (now + delta).replace(second=0, microsecond=0)
        wait_seconds = (next_start - now).seconds
        await channel.send(f"""This round of games for the {tourney.name} is now complete! The next round will start in {math.ceil(wait_seconds/60)} minutes.
Advancing teams:
{winners_string}""")
        await asyncio.sleep(wait_seconds)
    else:
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


def build_draft_embed(names, title="The Draft", footer="You must choose"):
    embed = discord.Embed(color=discord.Color.purple(), title=title)
    column_size = 7
    for i in range(0, len(names), column_size):
        draft = '\n'.join(names[i:i + column_size])
        embed.add_field(name="-", value=draft, inline=True)
    embed.set_footer(text=footer)
    return embed


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
    embed.add_field(name="█a██:", value=str(abs(hash(team.name)) % (10 ** 4)))
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
    if len(newteam_json["rotation"]) > 8:
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
    for player in newteam_json["rotation"]:
        newteam.add_pitcher(games.player(json.dumps(player)))

    return newteam

def team_from_message(command):
    newteam = games.team()
    roster = command.split("\n",1)[1].split("\n")
    newteam.name = roster[0].strip() #first line is team name
    newteam.slogan = roster[1].strip() #second line is slogan
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
                if game.over and ((key in main_controller.master_games_dic.keys() and main_controller.master_games_dic[key][1]["end_delay"] <= 8) or not key in main_controller.master_games_dic.keys()):                   
                    final_embed = game_over_embed(game)
                    if isinstance(user, str):
                        await channel.send(f"A game started by {user} just ended.")
                    elif user is not None:
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

    winning_team = game.teams['home'].name if game.teams['home'].score > game.teams['away'].score else game.teams['away'].name
    winstring = f"{game.teams['away'].score} to {game.teams['home'].score}\n"
    if game.victory_lap and winning_team == game.teams['home'].name:
        winstring += f"{winning_team} wins with a victory lap!"
    elif winning_team == game.teams['home'].name:
        winstring += f"{winning_team} wins, shaming {game.teams['away'].name}!"
    else:
        winstring += f"{winning_team} wins!"

    embed = discord.Embed(color=discord.Color.dark_purple(), title=title_string)
    embed.add_field(name="Final score:", value=winstring, inline=False)
    embed.add_field(name=f"{game.teams['away'].name} pitcher:", value=game.teams['away'].pitcher.name)
    embed.add_field(name=f"{game.teams['home'].name} pitcher:", value=game.teams['home'].pitcher.name)
    embed.set_footer(text=game.weather.emoji + game.weather.name)
    return embed

def get_team_fuzzy_search(team_name):
    team = games.get_team(team_name)
    if team is None:
        teams = games.search_team(team_name.lower())
        if len(teams) == 1:
            team = teams[0]
    return team

async def start_league_day(channel, league, partial = False):
    current_games = []
        
    games_to_start = league.schedule[str(league.day_to_series_num(league.day))]
    if league.game_length is None:
        game_length = games.config()["default_length"]
    else:
        game_length = league.game_length

    for pair in games_to_start:
        if pair[0] is not None and pair[1] is not None:
            away = get_team_fuzzy_search(pair[0])
            away.set_pitcher(rotation_slot=league.day)
            home = get_team_fuzzy_search(pair[1])
            home.set_pitcher(rotation_slot=league.day)

            this_game = games.game(away.finalize(), home.finalize(), length = game_length)
            this_game, state_init = prepare_game(this_game)

            state_init["is_league"] = True
            if not partial:
                series_string = "Series score:"
                state_init["title"] = f"{series_string} 0 - 0"
            else:
                state_init["title"] = "Interrupted series!"
            discrim_string = league.name     

            id = str(uuid4())
            current_games.append((this_game, id))
            main_controller.master_games_dic[id] = (this_game, state_init, discrim_string)

    ext = "?league=" + urllib.parse.quote_plus(league.name)

    if league.last_series_check(): #if finals
        await channel.send(f"The final series of the {league.name} regular season is starting now, at {config()['simmadome_url']+ext}")
        last = True

    else:
        await channel.send(f"The day {league.day} series of the {league.name} is starting now, at {config()['simmadome_url']+ext}")
        last = False

    if partial:
        missed_games = (league.day % league.series_length) - 1
        if missed_games == -1:
            missed_games = league.series_length - 1
        await league_day_watcher(channel, league, current_games, config()['simmadome_url']+ext, last, missed = missed_games)
    else:
        await league_day_watcher(channel, league, current_games, config()['simmadome_url']+ext, last)


async def league_day_watcher(channel, league, games_list, filter_url, last = False, missed = 0):
    league.active = True
    league.autoplay -= 1
    if league not in active_leagues:
        active_leagues.append(league)
    series_results = {}

    while league.active:
        queued_games = []
        while len(games_list) > 0:
            try:
                for i in range(0, len(games_list)):
                    game, key = games_list[i]
                    if game.over and ((key in main_controller.master_games_dic.keys() and main_controller.master_games_dic[key][1]["end_delay"] <= 8) or not key in main_controller.master_games_dic.keys()):
                        if game.teams['home'].name not in series_results.keys():
                            series_results[game.teams["home"].name] = {}
                            series_results[game.teams["home"].name]["wins"] = 0
                            series_results[game.teams["home"].name]["losses"] = 0
                            series_results[game.teams["home"].name]["run_diff"] = 0
                        if game.teams['away'].name not in series_results.keys():
                            series_results[game.teams["away"].name] = {}
                            series_results[game.teams["away"].name]["wins"] = 0
                            series_results[game.teams["away"].name]["losses"] = 0
                            series_results[game.teams["away"].name]["run_diff"] = 0

                        winner_name = game.teams['home'].name if game.teams['home'].score > game.teams['away'].score else game.teams['away'].name
                        loser_name = game.teams['away'].name if game.teams['home'].score > game.teams['away'].score else game.teams['home'].name
                        rd = int(math.fabs(game.teams['home'].score - game.teams['away'].score))

                        series_results[winner_name]["wins"] += 1
                        series_results[winner_name]["run_diff"] += rd

                        winner_dic = {"wins" : 1, "run_diff" : rd}

                        series_results[loser_name]["losses"] += 1
                        series_results[loser_name]["run_diff"] -= rd

                        loser_dic = {"losses" : 1, "run_diff" : -rd}

                        league.add_stats_from_game(game.get_team_specific_stats())
                        league.update_standings({winner_name : winner_dic, loser_name : loser_dic})
                        leagues.save_league(league)
                        final_embed = game_over_embed(game)
                        final_embed.add_field(name="Day:", value=league.day)
                        final_embed.add_field(name="Series score:", value=f"{series_results[game.teams['away'].name]['wins']} - {series_results[game.teams['home'].name]['wins']}")
                        await channel.send(f"A {league.name} game just ended!")                
                        await channel.send(embed=final_embed)
                        if series_results[winner_name]["wins"] + series_results[winner_name]["losses"] + missed < league.series_length:
                            queued_games.append(game)                           
                        games_list.pop(i)
                        break
            except:
                print("something went wrong in league_day_watcher")
            await asyncio.sleep(2)
        league.day += 1
        
        if len(queued_games) > 0:

            now = datetime.datetime.now()

            validminutes = [int((60 * div)/league.games_per_hour) for div in range(0,league.games_per_hour)]
            for i in range(0, len(validminutes)):
                if now.minute > validminutes[i]:
                    if i <= len(validminutes)-3:
                        if validminutes[i+1] == now.minute:
                            delta = datetime.timedelta(minutes= (validminutes[i+2] - now.minute))
                        else:
                            delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
                    elif i <= len(validminutes)-2:
                        if validminutes[i+1] == now.minute:
                            delta = datetime.timedelta(minutes= (60 - now.minute))
                        else:
                            delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
                    else:
                        delta = datetime.timedelta(minutes= (60 - now.minute))           

            next_start = (now + delta).replace(second=0, microsecond=0)
            wait_seconds = (next_start - now).seconds
                
            leagues.save_league(league)
            active_standings[league] = await channel.send(embed=league.standings_embed())
            await channel.send(f"The day {league.day} games for the {league.name} will start in {math.ceil(wait_seconds/60)} minutes.")
            await asyncio.sleep(wait_seconds)
            await channel.send(f"A {league.name} series is continuing now at {filter_url}")
            games_list = await continue_league_series(league, queued_games, games_list, series_results, missed)
        else:
            league.active = False

    if league.autoplay == 0 or config()["game_freeze"]: #if number of series to autoplay has been reached
        active_standings[league] = await channel.send(embed=league.standings_embed())
        await channel.send(f"The {league.name} is no longer autoplaying.")
        if config()["game_freeze"]:
            await channel.send("Patch incoming.")
        leagues.save_league(league)
        active_leagues.pop(active_leagues.index(league))
        return

    if last: #if last game of the season
        now = datetime.datetime.now()
        validminutes = [int((60 * div)/league.games_per_hour) for div in range(0,league.games_per_hour)]
        for i in range(0, len(validminutes)):
            if now.minute > validminutes[i]:
                if i <= len(validminutes)-3:
                    if validminutes[i+1] == now.minute:
                        delta = datetime.timedelta(minutes= (validminutes[i+2] - now.minute))
                    else:
                        delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
                elif i <= len(validminutes)-2:
                    if validminutes[i+1] == now.minute:
                        delta = datetime.timedelta(minutes= (60 - now.minute))
                    else:
                        delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
                else:
                    delta = datetime.timedelta(minutes= (60 - now.minute))           

        next_start = (now + delta).replace(second=0, microsecond=0)
        wait_seconds = (next_start - now).seconds
        await channel.send(f"This {league.name} season is now over! The postseason (with any necessary tiebreakers) will be starting in {math.ceil(wait_seconds/60)} minutes.")
        await asyncio.sleep(wait_seconds)
        await league_postseason(channel, league)

        #need to reset league to new season here

        return





    

    now = datetime.datetime.now()

    validminutes = [int((60 * div)/league.games_per_hour) for div in range(0,league.games_per_hour)]
    for i in range(0, len(validminutes)):
        if now.minute > validminutes[i]:
            if i <= len(validminutes)-3:
                if validminutes[i+1] == now.minute:
                    delta = datetime.timedelta(minutes= (validminutes[i+2] - now.minute))
                else:
                    delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
            elif i <= len(validminutes)-2:
                if validminutes[i+1] == now.minute:
                    delta = datetime.timedelta(minutes= (60 - now.minute))
                else:
                    delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
            else:
                delta = datetime.timedelta(minutes= (60 - now.minute))           

    next_start = (now + delta).replace(second=0, microsecond=0)
    wait_seconds = (next_start - now).seconds

    leagues.save_league(league)
    if league in active_standings.keys():
        await active_standings[league].unpin()
    active_standings[league] = await channel.send(embed=league.standings_embed())
    active_standings[league].pin()
    await channel.send(f"""This {league.name} series is now complete! The next series will be starting in {int(wait_seconds/60)} minutes.""")
    await asyncio.sleep(wait_seconds)

    await start_league_day(channel, league)

async def continue_league_series(league, queue, games_list, series_results, missed):
    for oldgame in queue:
        away_team = games.get_team(oldgame.teams["away"].name)
        away_team.set_pitcher(rotation_slot=league.day)
        home_team = games.get_team(oldgame.teams["home"].name)
        home_team.set_pitcher(rotation_slot=league.day)
        this_game = games.game(away_team.finalize(), home_team.finalize(), length = league.game_length)
        this_game, state_init = prepare_game(this_game)

        state_init["is_league"] = True
        series_string = f"Series score:"

        if missed <= 0:
            series_string = "Series score:"
            state_init["title"] = f"{series_string} {series_results[away_team.name]['wins']} - {series_results[home_team.name]['wins']}"
        else:
            state_init["title"] = "Interrupted series!"
        discrim_string = league.name

        id = str(uuid4())
        games_list.append((this_game, id))
        main_controller.master_games_dic[id] = (this_game, state_init, discrim_string)

    return games_list

async def league_postseason(channel, league):
    embed = league.standings_embed()
    embed.set_footer(text="Final Standings")
    await channel.send(embed=embed)
        

    tiebreakers = league.tiebreaker_required()       
    if tiebreakers != []:
        await channel.send("Tiebreakers required!")
        await asyncio.gather(*[start_tournament_round(channel, tourney) for tourney in tiebreakers])
        for tourney in tiebreakers:
            league.update_standings({tourney.winner.name : {"wins" : 1}})
            leagues.save_league(league)
        now = datetime.datetime.now()

        validminutes = [int((60 * div)/league.games_per_hour) for div in range(0,league.games_per_hour)]
        for i in range(0, len(validminutes)):
            if now.minute > validminutes[i]:
                if i <= len(validminutes)-3:
                    if validminutes[i+1] == now.minute:
                        delta = datetime.timedelta(minutes= (validminutes[i+2] - now.minute))
                    else:
                        delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
                elif i <= len(validminutes)-2:
                    if validminutes[i+1] == now.minute:
                        delta = datetime.timedelta(minutes= (60 - now.minute))
                    else:
                        delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
                else:
                    delta = datetime.timedelta(minutes= (60 - now.minute))           

        next_start = (now + delta).replace(second=0, microsecond=0)
        wait_seconds = (next_start - now).seconds
        await channel.send(f"Tiebreakers complete! Postseason starting in {math.ceil(wait_seconds/60)} minutes.")
        await asyncio.sleep(wait_seconds)
            

    tourneys = league.champ_series()
    await asyncio.gather(*[start_tournament_round(channel, tourney) for tourney in tourneys])
    champs = {}
    for tourney in tourneys:
        for team in tourney.teams.keys():
            if team.name == tourney.winner.name:
                champs[tourney.winner] = {"wins" : tourney.teams[team]["wins"]}
    world_series = leagues.tournament(f"{league.name} Championship Series", champs, series_length=7, secs_between_games=int(3600/league.games_per_hour), secs_between_rounds=int(7200/league.games_per_hour))
    world_series.build_bracket(by_wins = True)
    world_series.league = league
    now = datetime.datetime.now()

    validminutes = [int((60 * div)/league.games_per_hour) for div in range(0,league.games_per_hour)]
    for i in range(0, len(validminutes)):
        if now.minute > validminutes[i]:
            if i <= len(validminutes)-3:
                if validminutes[i+1] == now.minute:
                    delta = datetime.timedelta(minutes= (validminutes[i+2] - now.minute))
                else:
                    delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
            elif i <= len(validminutes)-2:
                if validminutes[i+1] == now.minute:
                    delta = datetime.timedelta(minutes= (60 - now.minute))
                else:
                    delta = datetime.timedelta(minutes= (validminutes[i+1] - now.minute))
            else:
                delta = datetime.timedelta(minutes= (60 - now.minute))           

    next_start = (now + delta).replace(second=0, microsecond=0)
    wait_seconds = (next_start - now).seconds
    await channel.send(f"The {league.name} Championship Series is starting in {math.ceil(wait_seconds/60)} minutes!")
    await asyncio.sleep(wait_seconds)
    await start_tournament_round(channel, world_series)
    league.champion = world_series.winner.name
    leagues.save_league(league)
    season_save(league)
    league.season_reset()



client.run(config()["token"])
