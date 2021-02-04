# matteo-the-prestige
# simsim discord bot

blaseball, blaseball, is back! in an unofficial capacity. this project is completely unaffiliated with the game band.

we have custom players (generated by onomancer), custom teams, custom leagues, all set up in discord and watchable at https://simsim.sibr.dev! 

if you would like to add matteo to your server to be able to set up teams and games, you can do so with this link: https://discord.com/api/oauth2/authorize?client_id=789956166796574740&permissions=388160&scope=bot

accepting pull requests, check the issues for to-dos.

## Table of Contents:
- [FAQ](#FAQ)
- [commands](#commands)


## FAQ (this FAQ is a work in progress and will be expanded over time):
- Q: Why have the teams in my league played an uneven amount of games/why are some teams not scheduled for games for some weeks?  
  A: Scheduling algorithms are really hard and the way xvi chose to do it involves some teams having byes for some series of the season, it'll even out by the end and every team will play the same number of games.
  
- Q: My league stopped playing randomly and I don't know why, what should I do?  
  A: There were probably server issues or a patch went out, use the startleague command again and things should resume from where they left off.

- Q: What should I do if my question isn't answered by this FAQ, this readme, or the help text for the commands, or I find a bug?  
  A: Please submit your issue or bug to this form and Artemis will pass it along if it's something we can do anything about. https://forms.gle/PjbpfT46yuMDGca46


## commands: (everything here is case sensitive, and can be prefixed with either m; or m!)
### team commands:
#### creation and deletion:
- m;saveteam
  - saves a team to the database allowing it to be used for games. use this command at the top of a list with entries separated by new lines:
	- the first line of the list is your team's name.
	- the second line is the team's icon and slogan, generally this is an emoji followed by a space, followed by a short slogan.
	- the third line must be blank.
	- the next lines are your batters' names in the order you want them to appear in your lineup, lineups can contain any number of batters between 1 and 12.
	- then another blank line separating your batters and your pitchers.
	- the final lines are the names of the pitchers in your rotation, rotations can contain any number of pitchers between 1 and 8.
  - if you did it correctly, you'll get a team embed with a prompt to confirm. hit the 👍 and your team will be saved!
- m;deleteteam [teamname] (requires team ownership)
  - allows you to delete the team with the provided name. you'll get an embed with a confirmation to prevent accidental deletions. hit the 👍 and your team will be deleted.
- m;import
  - imports an onomancer collection as a new team. you can use the new onomancer simsim setting to ensure compatibility. similarly to saveteam, you'll get a team embed with a prompt to confirm, hit the 👍 and your team will be saved!
#### editing (all of these commands require ownership and exact spelling of the team name):
- m;replaceplayer [team name] [player to remove] [player to add]
  - replaces a player on your team with a new player. if there are multiple copies of the same player on a team this will only replace the first one. use this command at the top of a list with entries separated by new lines:
    - the name of the team you want to replace the player on.
	- the name of the player you want to remove from the team.
	- the name of the player you want to replace them with.
- m;addplayer batter/pitcher [team name] [player name]
  - adds a new player to the end of your team, either in the lineup or the rotation depending on which version you use. use addplayer batter or addplayer pitcher at the top of a list with entries separated by new lines:
    - the name of the team you want to add the player to.
	- the name of the player you want to add to the team.
- m;moveplayer (batter/pitcher) [team name] [player name] [new lineup/rotation position number]
  - moves a player within your lineup or rotation. if you want to instead move a player from your rotation to your lineup or vice versa, use m;swapsection instead.
  - you can optionally specify batter or pitcher if you have a player in both your rotation and lineup and you want to move a specific one. you don't need to include it if you only have one copy of the player on your team.  
  - use this command at the top of a list with entries separated by new lines:
    - the name of the team you want to move the player on.
	- the name of the player you want to move.
	- the position you want to move them too, indexed with 1 being the first position of the lineup or rotation. all players below the specified position in the lineup or rotation will be pushed down.
- m;swapsection [team name] [player name]
  - swaps a player from your lineup to the end of your rotation or your rotation to the end of your lineup. use this command at the top of a list with entries separated by new lines:
    - the name of the team you want to swap the player on.
	- the name of the player you want to swap.
- m;removeplayer [team name] [player name]	
  - removes a player from your team. if there are multiple copies of the same player on a team this will only delete the first one. use this command at the top of a list with entries separated by new lines:
	- the name of the team you want to remove the player from.
	- the name of the player you want to remove.
#### viewing and searching:  
- m;showteam [name]
  - shows the lineup, rotation, and slogan of any saved team in a discord embed with primary stat star ratings for all of the players. this command has fuzzy search so you don't need to type the full name of the team as long as you give enough to identify the team you're looking for.
- m;searchteams [searchterm]
  - shows a paginated list of all teams whose names contain the given search term.
- m;showallteams
  - shows a paginated list of all teams available for games which can be scrolled through.	
  
### game commands:
- m;startgame --day # or -d #
  - starts a game with premade teams made using saveteam. provides a link to the website where you can watch the game. 
  - the --day/-d is optional, if used it'll force the game to use the #th spot in each team's rotations. if this number is larger than the number of pitchers in one or both of the teams' rotations it'll wrap around. if it is not used pitchers will be chosen randomly from the teams' rotations.
  - use this command at the top of a list with entries separated by new lines:
	- the away team's name.
	- the home team's name.
	- optionally, the number of innings, which must be greater than 2 and less than 201. if not included it will default to 9.
  -	this command has fuzzy search so you don't need to type the full name of the team as long as you give enough to identify the team you're looking for.
- m;randomgame
  - starts a 9-inning game between 2 entirely random teams. embrace chaos!
- m;starttournament --rounddelay #
  - starts a randomly seeded tournament with the provided teams, automatically adding byes as necessary. all series have a 5 minute break between games. the current format is: best of 5 until the finals which are best of 7. 
  - the --rounddelay is optional, if used, # must be between 1 and 120 and it'll set the delay between rounds to be # minutes. if not included it will default to 10.
  - use this command at the top of a list with entries separated by new lines:
    - the name of the tournament.
	- the name of each participating team on its own line.

### draft commands
- m;startdraft
  - starts a draft with an arbitrary number of participants. use this command at the top of a list with entries separated by new lines:
	- for each participant's entry you need three lines:
	  - their discord @
	  - their team name
	  - their team slogan
	- post this with all three of these things for all participants and the draft will begin.
  - the draft will begin once all participants have given a 👍 and will proceed in the order that participants were entered. each participant will select 12 hitters and 1 pitcher from a pool of 20 random players which will refresh automatically when it becomes small.
- m;draft [name]
  - use this on your turn during a draft to pick your player.
  - you can also just use a 'd' instead of the full command.

### league commands
- all of these commands are for leagues that have already been started. to start a league, click the 'create a league' button on the website and fill out the info for your league there, then use the m;claimleague command in discord to set yourself as the owner.
- commissioner commands (all of these except for m;claimleague require ownership of the specified league):
  - m;claimleague [league name]
    - sets yourself as the owner of an unclaimed league created on the website. make sure to do this as soon as possible since if someone does this before you, you will not have access to the league.
  - m;addleagueowner [league name]
    - use this command at the top of a list of @mentions, with entries separated by new lines, of people you want to have owner powers in your league.
  - m;startleague [league name] --queue #/-q # --noautopostseason
    - send this command with the number of games per hour you want on the next line, minimum 1 (one game every hour), maximum 12 (one game every 5 minutes, uses spillover rules).
	- starts the playing of league games at the pace specified, by default will play the entire season and the postseason unless an owner pauses the league with the m;pauseleague command. 
	- if you use the --queue #/-q # flag, the league will only play # series' at a time before automatically pausing until you use this command again, by default it will play the entire season unless stopped.
	- if you use the --noautopostseason flag, instead of starting automatically, the league will pause at the end of the regular season and not start the postseason until you use this command again.
  - m;pauseleague [league name]
    - pauses the specified league after the current series finishes until the league is started again with m;startleague.
  - m;leagueseasonreset [league name]
    - completely scraps the given league's current season, resetting everything to day 1 of the current season. make sure to use m;startleague again to restart the season afterwards.
- general commands (all of these can be used by anyone):
  - m;leaguestandings [league name] --season #/-s #
    - displays the current standings for the specified league.
	- by default this will display the standings for the current season but if the --season #/-s # flag is set it will instead display the standings for the #th season instead for viewing historical standings.
  - m;leaguewildcard [league name]
    - displays the wild card standings for the specified league. if the league doesn't have wild cards, it will instead tell you that.
  - m;leagueschedule [league name]
    - displays the upcoming schedule for the specified league. shows the current series and the next three series after that for every team.
  - m;teamchedule [league name] [team name]
    - displays the upcoming schedule for the specified team within the specified league. shows the current series and the next six series after that for the given team.
  - m;leagueleaders [league name] [stat]
    - displays a league's leaders in the given stat.
	- the currently available starts are:
	  - for batters: avg (batting average), slg (slugging percentage), obp (on-base percentage), ops (on-base plus slugging). 
	  - for pitchers era (earned run average), whip (walks and hits per innings pitched), kper9 (strikeouts per 9 innings), bbper9 (walks per 9 innings), kperbb (strikeout to walk ratio).
### player commands:	 
- m;showplayer [name]
  - displays any name's stars, there's a limit of 70 characters. that should be *plenty*. note: if you want to lookup a lot of different players you can do it on onomancer instead of spamming this command a bunch and clogging up discord: https://onomancer.sibr.dev/reflect
- m;idolize [name]
  - records any name as your idol, mostly for fun.
- m;showidol 
  - displays your idol's name and stars in a discord embed.
  
### other commands:
- m;help [command]
  - shows instructions for a given command. if no command is provided, it will instead provide a list of all of the commands that instructions can be provided for.    
- m;credit
  - shows artist credit for matteo's avatar.  
- m;roman [number]
  - converts any natural number less than 4,000,000 into roman numerals, this one is just for fun.

## patreon!

these folks are helping me a *ton* via patreon, and i cannot possibly thank them enough:
- Ale Humano
- Chris Denmark
- Astrid Bek
- Kameleon
- Ryan Littleton
- Evie Diver
- iliana etaoin
- yooori

## Attribution

Twemoji is copyright 2020 Twitter, Inc and other contributors; code licensed under [the MIT License](http://opensource.org/licenses/MIT), graphics licensed under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)
