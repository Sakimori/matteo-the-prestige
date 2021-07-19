# matteo-the-prestige
# sim16 + discord bot: baseball simulation

Sim16 is a discord and website based online baseball simulator, every name has randomly generated stats which you can use to make custom teams and custom leagues, all created and set up in discord and watchable at http://sim16.Sakimori.space! 

If you would like to add the bot to your server to be able to set up teams and games, you can do so with this link: https://discord.com/api/oauth2/authorize?client_id=789956166796574740&permissions=388160&scope=bot

If you would like to chat with the devs or join the main community for the bot that can all be found in this discord: https://discord.gg/ux6Drk8Bp7

If you have any feedback or think you've found a bug with the bot, the best way to do so is via this form: https://docs.google.com/forms/d/e/1FAIpQLSc63J2irST7bI-USu8Xd_yv16UwWtVnipfAU0r-1b46ME-UuA/viewform

Accepting pull requests, check the issues for to-dos, if you have an idea for an enhancement you'd like to make to the bot, run it by the devs in discord first.


# Table of Contents
* [FAQ](https://github.com/Sakimori/matteo-the-prestige#faq-this-faq-is-a-work-in-progress-and-will-be-expanded-over-time)
* [Commands](https://github.com/Sakimori/matteo-the-prestige#commands-everything-here-is-case-sensitive-and-can-be-prefixed-with-either-m-or-m)
  - [Team Commands](https://github.com/Sakimori/matteo-the-prestige#team-commands)
    - [Creation and deletion](https://github.com/Sakimori/matteo-the-prestige#creation-and-deletion)
    - [Editing](https://github.com/Sakimori/matteo-the-prestige#editing-all-of-these-commands-require-ownership-and-exact-spelling-of-the-team-name)
    - [Viewing and Searching](https://github.com/Sakimori/matteo-the-prestige#viewing-and-searching)
  - [Game Commands](https://github.com/Sakimori/matteo-the-prestige#game-commands)
	- [Individual Game Commands](https://github.com/Sakimori/matteo-the-prestige#individual-game-commands)
	- [Tournament Commands](https://github.com/Sakimori/matteo-the-prestige#tournament-commands)
	- [OBL Commands](https://github.com/Sakimori/matteo-the-prestige#obl-commands)
	- [Draft Commands](https://github.com/Sakimori/matteo-the-prestige#draft-commands)
	- [League Commands](https://github.com/Sakimori/matteo-the-prestige#league-commands)	
  - [Player Commands](https://github.com/Sakimori/matteo-the-prestige#player-commands)
    - [General Player Commands](https://github.com/Sakimori/matteo-the-prestige#general-player-commands)
    - [Archetpe Commands](https://github.com/Sakimori/matteo-the-prestige#archetype-commands)
  - [Other Commands](https://github.com/Sakimori/matteo-the-prestige#other-commands)
* [Archetypes](https://github.com/Sakimori/matteo-the-prestige#archetypes)
* [Weathers](https://github.com/Sakimori/matteo-the-prestige#weathers)
* [Patreon](https://github.com/Sakimori/matteo-the-prestige#patreon)
* [Attribution](https://github.com/Sakimori/matteo-the-prestige#attribution)
  
## FAQ:
- Q: What is sim16?  
  A: This twitter thread provides outlines the basics pretty well, give it a read: https://twitter.com/FHelltiger/status/1374119998780755969?s=20

- Q: How do I get started with sim16?  
  A: If you aren't already in a discord server that has the bot, add it to your server with the link at the start. Once you've done that or if you're already in a server with it, start by making a team using m;saveteam, you can see a description of how to use this here in the readme or by using m;help saveteam. Once you have a team, I recommend looking into the OBL starting my doing m;oblhelp. Other than that, I recommend joining the main discord above and having a look at the #lfg channel there if you're interested in participating in a league, otherwise just look around the readme and do what sounds fun to you!

- Q: I'm trying to make a league on the website but when I click the 'submit' button it doesn't do anything and doesn't give an error message.  
  A: This is a known issue, to avoid it make sure you have an even number of divisions and subleagues and an equal number of teams in each division. These are all requirements for a league and sometimes if some of them aren't met the submit button will fail silently. If you're still having this issue after doing all of this correctly please submit a bug report via the form.

- Q: What is the maximum and minimum sizes for teams?  
  A: The minimum size is 1 batter and 1 pitcher, the maximum size is 20 batters and 8 pitchers.

- Q: What does [weather] do?  
  A: See the weathers section of the readme for a description of all the weathers except the current patch's weathers, those you have to figure out yourself (or just ask and someone will probably tell you).

- Q: My league stopped playing randomly and I don't know why, what should I do?  
  A: There were probably server issues or a patch went out, use the startleague command again and things should resume from where they left off, if this doesn't fix it submit an issue to the issue reporting form and we can troubleshoot it for you.  

- Q: Why aren't all the teams playing on every day of my league/why do teams have an uneven amount of games played in my league?  
  A: Scheduling algorithms are hard and due to how this one was coded, sometimes teams have bye weeks and rest for some games the season, this should all even out by the end of the season and each team will play the same number of games.

- Q: What should I do if my question isn't answered by this FAQ, this readme, or the help text for the commands, or I find a bug?  
  A: If you have any mechanical questions, feel free to stop by the sim16 discord linked at the beginning and ask your question in the lobby there. If you have an issue or think you've found a bug, submit it to the issue reporting form and we'll look into it.


## Commands: (Everything here is case sensitive, and can be prefixed with either m; or m!)
### Team Commands:
#### Creation and Deletion:
- m;saveteam
  - Saves a team to the database allowing it to be used for games. Use this command at the top of a list with entries separated by new lines:
	- The first line of the list is your team's name.
	- The second line is the team's icon and slogan, generally this is an emoji followed by a space, followed by a short slogan.
	- The third line must be blank.
	- The next lines are your batters' names in the order you want them to appear in your lineup, lineups can contain any number of batters between 1 and 20.
	- Then another blank line separating your batters and your pitchers.
	- The final lines are the names of the pitchers in your rotation, rotations can contain any number of pitchers between 1 and 8.
  - If you did it correctly, you'll get a team embed with a prompt to confirm. hit the 👍 and your team will be saved!
- m;deleteteam [teamname] (requires team ownership)
  - Allows you to delete the team with the provided name. You'll get an embed with a confirmation to prevent accidental deletions. Hit the 👍 and your team will be deleted.
- m;import
  - Imports an onomancer collection as a new team. you can use the new onomancer sim16 setting to ensure compatibility. Similarly to saveteam, you'll get a team embed with a prompt to confirm, hit the 👍 and your team will be saved!
#### Editing (all of these commands require ownership and exact spelling of the team name):
- m;replaceplayer [team name] [player to remove] [player to add]
  - Replaces a player on your team with a new player. if there are multiple copies of the same player on a team this will only replace the first one. Use this command at the top of a list with entries separated by new lines:
    - The name of the team you want to replace the player on.
	- The name of the player you want to remove from the team.
	- The name of the player you want to replace them with.
- m;addplayer batter/pitcher [team name] [player name]
  - Adds a new player to the end of your team, either in the lineup or the rotation depending on which version you use. use addplayer batter or addplayer pitcher at the top of a list with entries separated by new lines:
    - The name of the team you want to add the player to.
	- The name of the player you want to add to the team.
- m;moveplayer (batter/pitcher) [team name] [player name] [new lineup/rotation position number]
  - Moves a player within your lineup or rotation. If you want to instead move a player from your rotation to your lineup or vice versa, use m;swapsection instead.
  - You can optionally specify batter or pitcher if you have a player in both your rotation and lineup and you want to move a specific one. You don't need to include it if you only have one copy of the player on your team.  
  - Use this command at the top of a list with entries separated by new lines:
    - The name of the team you want to move the player on.
	- The name of the player you want to move.
	- The position you want to move them too, indexed with 1 being the first position of the lineup or rotation. All players below the specified position in the lineup or rotation will be pushed down.
- m;swapsection [team name] [player name]
  - Swaps a player from your lineup to the end of your rotation or your rotation to the end of your lineup. Use this command at the top of a list with entries separated by new lines:
    - The name of the team you want to swap the player on.
	- The name of the player you want to swap.
- m;removeplayer [team name] [player name]	
  - Removes a player from your team. if there are multiple copies of the same player on a team this will only delete the first one. Use this command at the top of a list with entries separated by new lines:
	- The name of the team you want to remove the player from.
	- The name of the player you want to remove.
#### Viewing and Searching:  
- m;showteam [name]
  - Shows the lineup, rotation, and slogan of any saved team in a discord embed with primary stat star ratings for all of the players. This command has fuzzy search so you don't need to type the full name of the team as long as you give enough to identify the team you're looking for.
- m;searchteams [searchterm]
  - Shows a paginated list of all teams whose names contain the given search term.
- m;showallteams
  - Shows a paginated list of all teams available for games which can be scrolled through. 
  
[Return to the top](https://github.com/Sakimori/matteo-the-prestige#matteo-the-prestige)
  
### Game Commands:
#### Individual Game Commands:
- m;startgame --day # or -d #, -w [Weather Name] or --weather [Weather Name], -v [Commentator Name] or --voice [Commentator Name]
  - Starts a game with premade teams made using saveteam. Provides a link to the website where you can watch the game. 
  - The --day/-d is an optional flag, if used it'll force the game to use the #th spot in each team's rotations. If this number is larger than the number of pitchers in one or both of the teams' rotations it'll wrap around. If it is not used pitchers will be chosen randomly from the teams' rotations.
  - The -w/--weather is the same, if used it'll force the game to be the specified weather, weathers must be spelled out exactly with the first letter capitalized, see further down for a full list of weathers and their exact names.
  - The -v/--voice flag forces a specified commentator for the game, the current options are: default, The Goddesses, The New Guy
  - Use this command at the top of a list with entries separated by new lines:
	- The away team's name.
	- The home team's name.
	- Optionally, the number of innings, which must be greater than 2 and less than 201. If not included it will default to 9.
  -	This command has fuzzy search so you don't need to type the full name of the team as long as you give enough to identify the team you're looking for.
- m;randomgame
  - Starts a 9-inning game between 2 entirely random teams. Embrace chaos!
#### Tournament Commands:
- m;starttournament --rounddelay #, --bestof #, --finalsbestof #, --seeding 
  - Starts a randomly seeded tournament with the provided teams, automatically adding byes as necessary. All series have a 5 minute break between games. The current default format is teams seeded randomly best of 5 until the finals which are best of 7 but this can be adjusted by adding the bestof and finalsbestof flags. 
  - The --rounddelay is optional, if used, # must be between 1 and 120 and it'll set the delay between rounds to be # minutes. If not included it will default to 10.
  - The --seeding flag changes the seeding of the tournament, currently there is only one option '--seeding stars' which seeds the teams based on average primary attribute stars instead of randomly. This is currently the only option but more may be added in the future.
  Use this command at the top of a list with entries separated by new lines:
    - The name of the tournament.
	- The name of each participating team on its own line.	
#### OBL Commands:
- m;oblhelp
  - Shows the explanation for what the OBL is and how to participate.
- m;oblteam [team name]
  - Displays a team's rank, current OBL points, and current bounty board.
- m;oblrival [team name] [rival team]
  - Sets your team's OBL rival, this can be changed at any time and requires ownership. your rival is purely cosmetic but will show on your team card and be marked with a special marker if they're on your list of opponents. Each team needs to be on a new line below the command.
- m;oblwins [team name]
  - Displays a trophy case with all teams that the given team has won points from.
- m;oblstandings
  - Displays the 15 teams with the most OBL points in this meta-season.  
#### Draft Commands
- m;startdraft -d #, -m # -t #, -p #, -w #, -c #
  - Starts a draft with an arbitrary number of participants. By default teams will draft in order from a pool of 20 players until there are 5 left at which point the pool will refresh. By default each team will select 13 players, 12 hitters and 1 pitcher in that order, many of these things can be modified via the flags.
  - The -d # flag sets the size of the draft pool, by default this is 20.
  - The -m # flag sets the minimum size the pool can reach before resetting, by default this is 5, this cannot be set to the same as -d but if set to one lower the pool will refresh after every pick.
  - The -t # flag changes the size of the teams, the number of batters will be this number minus the number provided for -p, by default 1.
  - The -p # flag sets the number of pitchers each team will have, by default this is 1 but you may want to change this if drafting with the intention to use a team in a league.
  - The -w # flag sets the wait time before the draft skips someone's pick for inactivity, in seconds. By default this is 120, or 2 mintutes.
  - The -c # flag sets the 'chaos ratio', must be a number between 0 and 1 with 0 being 0% chaos, or 100% real player names, and 1 being 100% chaos, or 100% onomancer names. By default this is set to .25.
  - Use this command with any chosen flags at the top of a list with entries separated by new lines:
	- For each participant's entry you need three lines:
	  - Their discord @
	  - Their team name
	  - Their team slogan
	- Post this with all three of these things for all participants and the draft will begin.
  - The draft will begin once all participants have given a 👍 and will proceed in the order that participants were entered. Each participant will select 12 hitters and 1 pitcher from a pool of 20 random players which will refresh automatically when it becomes small.
-m;draftflags
  - Shows dectiptions of all of draft flags for reference since there are a lot of them.
- m;draft [name]
  - Use this on your turn during a draft to pick your player.
  - You can also just use a 'd' instead of the full command. 
#### League Commands
- All of these commands are for leagues that have already been started. To start a league, click the 'create a league' button on the website and fill out the info for your league there, then use the m;claimleague command in discord to set yourself as the owner.
- Commissioner Commands (all of these except for m;claimleague require ownership of the specified league):
  - m;claimleague [league name]
    - Sets yourself as the owner of an unclaimed league created on the website. Make sure to do this as soon as possible since if someone does this before you, you will not have access to the league.
  - m;addleagueowner [league name]
    - Use this command at the top of a list of @mentions, with entries separated by new lines, of people you want to have owner powers in your league.
  - m;startleague [league name] --queue #/-q # -a/--autopostseason, -s/--skippostseason
    - Send this command with the number of games per hour you want on the next line, minimum 1 (one game every hour), maximum 12 (one game every 5 minutes, uses spillover rules).
	- Starts the playing of league games at the pace specified, by default will play the entire season and the postseason unless an owner pauses the league with the m;pauseleague command. 
	- If you use the --queue #/-q # flag, the league will only play # series' at a time before automatically pausing until you use this command again, by default it will play the entire season unless stopped.
	- If you use the --autopostseason/-a flag, the league will automatically play the postseason after the regular season, if not use you will need to use m;startleague again after the season to start the postseason.
	- If you use the --skippostseason/-s flag, the league will not have an automatic postseason. Only use this flag if you're absolutely sure this is what you want to do, for example if you want to run a custom post-season. 
  - m;pauseleague [league name]
    - Pauses the specified league after the current series finishes until the league is started again with m;startleague.
  - m;leagueseasonreset [league name]
    - Completely scraps the given league's current season, resetting everything to day 1 of the current season. Make sure to use m;startleague again to restart the season afterwards.
  - m;leaguereplaceteam [league name] [team to remove] [team to add]
    - Replaces a team in a league with a new team. Can only be done in the offseason. Sent this command with the team league name on the line of the command and the teams to remove/add on the next lines. Replaces a team in a league with a new team. Can only be done in the offseason.
  - m;swapteams [league name] [team a] [team b]
    - Swaps the division/conference of two teams in a league. Sent this command with the team league name on the line of the command and the teams to swap on the next lines.    
- General Commands (all of these can be used by anyone):
  - m;leaguestandings [league name] --season #/-s #
    - Displays the current standings for the specified league.
	- By default this will display the standings for the current season but if the --season #/-s # flag is set it will instead display the standings for the #th season instead for viewing historical standings.
  - m;leaguewildcard [league name]
    - Displays the wild card standings for the specified league. If the league doesn't have wild cards, it will instead tell you that.
  - m;leagueschedule [league name]
    - Displays the upcoming schedule for the specified league including the weather forecast. Shows the current series and the next three series after that for every team.
  - m;teamchedule [league name] [team name]
    - Displays the upcoming schedule for the specified team within the specified league including the weather forecast. Shows the current series and the next six series after that for the given team.
  - m;leagueleaders [league name] [stat]
    - Put the stat you want to display on a new line. Displays a league's leaders in the given stat.
	- The currently available starts are:
	  - For batters: avg (batting average), slg (slugging percentage), obp (on-base percentage), ops (on-base plus slugging), home runs, walks drawn. 
	  - For pitchers era (earned run average), whip (walks and hits per innings pitched), kper9 (strikeouts per 9 innings), bbper9 (walks per 9 innings), kperbb (strikeout to walk ratio), eramin (players with the worst earned run average). 
  - m;leaguesub [league name]
    - Posts all league feed events to this channel, in addition to the channel the league was started in. Run again to unsubscribe.

[Return to the top](https://github.com/Sakimori/matteo-the-prestige#matteo-the-prestige)

### Player Commands:
#### General Player Commands:	 
  - m;showplayer [name]
    - Displays any name's stars, there's a limit of 70 characters which is the max which can be used on a team. Note: if you want to lookup a lot of different players you can do it at the source on onomancer instead of spamming this command a bunch and clogging up discord: https://onomancer.sibr.dev/reflect
  - m;idolize [name]
    - Records any name as your idol, mostly for fun.
  - m;showidol 
    - Displays your idol's name and stars in a discord embed.
#### Archetype Commands:
- Archetypes are modifications that affect a player only on a specific team, they all have positives and negatives and are intended to help provide flavor to teams. A full list of archetypes can be found [here](https://github.com/Sakimori/matteo-the-prestige#archetypes) or with the m;archetypehelp command.
  - m;archetype [team name] [player name] [archetype name]
    - Assigns an archetype to a player on a team, put each part of the command on a seperate line in that order. You can either use the full name or the short name for this command, both will work.
  - m;archetypehelp ([archetype name])
    - Provides a list of archetypes if no archetype is specified or gives information about the specified archetype. 
  - m;teamarchetypes [team name]
    - Lists all players with an archetype on the given team and what their archetype is.
  
[Return to the top](https://github.com/Sakimori/matteo-the-prestige#matteo-the-prestige)
  
### Other Commands:
- m;help [command]
  - Shows instructions for a given command. If no command is provided, it will instead provide a list of all of the commands that instructions can be provided for.    
- m;credit
  - Shows artist credit for Matteo's avatar.  
- m;roman [number]
  - Converts any natural number less than 4,000,000 into roman numerals, this one is just for fun. 
  
[Return to the top](https://github.com/Sakimori/matteo-the-prestige#matteo-the-prestige)

## Archetypes
- All current archetypes are listed here with short descriptions and their short names, all archetypes can be assigned to pitchers or hitters but they all currently primarily affect one or the other so they will be noted as such here:
  - Jack of All Trades/basic (all): Master of none. No bonuses or penalties. This is the archetype each player is given by default and you can assign this to remove another archetype.
  - Three True Outcomes/pure power (batter): Better at getting walks and home runs at the cost of striking out more.
  - Contact Specialist/contact (batter): Better at getting hits at the cost of power.
  - Sprinter/speed (batter): Better at baserunning and defense at the cost of home run power.
  - They've Got the Stuff/velocity (pitcher): Better at getting outs at the cost of giving up more walks.
  - Puppetmaster/control (pitcher): Better at getting weak contact at the cost of allowing more hits.

[Return to the top](https://github.com/Sakimori/matteo-the-prestige#matteo-the-prestige)

## Weathers
- All current sim16 weathers are listed here with a short description of their effects except for the most recent weathers whose effects remain a mystery.
  - Supernova 🌟: Makes all pitchers pitch worse, significantly increased effect on stronger pitchers.
  - Midnight 🕶: Significantly increased the chance that players will attempt to steal a base.
  - Blizzard ❄: Occasionally causes the team's pitcher to bat in place of the scheduled batter.
  - Slight Tailwind 🏌️‍♀: Occasionally batters get a mulligan and start the at bat over if they would have gotten out, significantly more likely to happen for weaker batters. 
  - Thinned Veil 🌌: When a player hits a dinger, they end up on the base corresponding to the number of runs the dinger scored, 1st base if it's a solo home run, up to none base if it's a grand slam, resulting in 5 runs scoring.
  - Twilight 👻: Occasionally turns outs into hit by causing the ball to go ethereal, preventing the fielder from catching it.
  - Drizzle 🌧: Causes each inning to start with the previous inning's final batter on second base.
  - Heat Wave 🌄: Occasionally causes pitchers to be relieved by a random player from the lineup.
  - Breezy 🎐: Occasionally swaps letters of a player's name, altering their name for the remainder of the game and changing their stats.
  - Starlight 🌃: The stars are displeased with dingers and will cancel most of them out by pulling them foul.
  - Meteor Shower 🌠: Has a chance to warp runners on base to none base causing them to score.
  - Hurricane 🌀: Flips the scoreboard every few innings.
  - Tornado 🌪: Occasionally shuffles baserunners around to different bases.
  - Torrential Downpour ⛈: The game does not end until one team scores X runs where X is the original inning count of the game, 9 by default.
  - Summer Mist 🌁: When a player hits into an out, they have a chance to get lost in the mist and be temporarily removed from the lineup. If another player gets lost in the mist the first player returns and takes the newly lost player's spot in the lineup.
  - Leaf Eddies 🍂: The visiting team plays all of their outs in a row without inning breaks, then the home team does the same, if the game ends tied, each team plays sudden death 1-out 'golden run' innings until the game is decided.
  - Smog 🚌: Picks a new random weather at the beginning of each inning from: Supernova, Midnight, Slight Tailwind, Twilight, Thinned Veil, Drizzle, Breezy, Starlight, Meteor Shower, Hurricane, Tornado, Summer Mist, and Dusk.
  - Dusk 🌆: New patch weather, its effects will be revealed next time a new weather in implemented.
  
[Return to the top](https://github.com/Sakimori/matteo-the-prestige#matteo-the-prestige)

## Patreon!

these folks are helping me a *ton* via patreon, and i cannot possibly thank them enough:
- Ale Humano
- Chris Denmark
- Astrid Bek
- Kameleon
- Ryan Littleton
- Evie Diver
- iliana etaoin
- yooori
- Bend
- ALC

## Attribution

Twemoji is copyright 2020 Twitter, Inc and other contributors; code licensed under [the MIT License](http://opensource.org/licenses/MIT), graphics licensed under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 

[Return to the top](https://github.com/Sakimori/matteo-the-prestige#matteo-the-prestige)
