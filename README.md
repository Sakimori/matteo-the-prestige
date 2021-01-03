# matteo-the-prestige
# simsim discord bot

blaseball, blaseball, is back! in an unofficial capacity. this is completely unaffiliated with the game band.

custom players, custom teams, custom leagues (that last one is coming soon™) all set up in discord and watchable at https://simsim.sibr.dev, all powered by this bot and onomancer. 

if you would like to add Matteo to your server to be able to set up teams and games, you can do so with this link: https://discord.com/api/oauth2/authorize?client_id=789956166796574740&permissions=388160&scope=bot

accepting pull requests, check the issues for to-dos.


## commands: (everything here is case sensitive, and can be prefixed with either m; or m!)

### team commands:

#### creation and deletion:
- m;saveteam
  - saves a team to the database allowing it to be used for games. use this command at the top of a list with each of these in a new line:
	- the team's name (cannot contain emoji).
	- the team's icon and slogan, generally this is an emoji followed by a space, followed by a short slogan.
	- a blank line.
	- the batters' names in the order you want them to appear in your lineup, each in its own line. lineups can contain any number of batters between 1 and 12.
	- a blank line.
	- the pitchers' names in the order you want them to appear in your rotation. rotations can contain any number of pitchers between 1 and 8.
  - if you did it correctly, you'll get a team embed with a prompt to confirm. hit the 👍 and it'll be saved.
- m;deleteteam [teamname]
  - allows you to delete the team with the provided name. requires team ownership. gives a confirmation first to prevent accidental deletions.
- m;import
  - imports an onomancer collection as a new team. you can use the new onomancer simsim setting to ensure compatibility.

#### editing (all of these commands require ownership of the team used):
- m;addplayer batter/pitcher [team name] [player name]
  - adds a new player to the end of your team, either in the lineup or rotation depending on which version you use. use addplayer batter or addplayer pitcher at the top of a list with each of these in a new line:
    -the name of the team you want to add the player to.
	-the name of the player you want to add to the team.
- m;moveplayer [team name] [player name] [new lineup/rotation position number]
  - changes the position of a player in the lineup and rotation. use this command at the top of a list with each of these in a new line:
    - the name of the team you want to move the player on.
	- the name of the player you want to move.
	- the position you want to move them too, indexed with 1 being the first position of the lineup or rotation.
- m;swapsection [team name] [player name]
  - swaps a player from the lineup to rotation or rotation to lineup. use this command at the top of a list followed by each of these in a new line:
    - the name of the team you want to swap the player on.
	- the name of the player you want to swap.
- m;removeplayer [team name] [player name]	
  - removes a player from your lineup or rotation. if there are multiple copies of the same player on a team this will delete the first one. use this command at the top of a list with each of these in a new line:
	- the name of the team you want to remove the player from.
	- the name of the player you want to remove.

#### viewing and searching:  
- m;showteam [name]
  - shows information about any saved team.
- m;showallteams
  - shows a paginated list of all teams available for games which can be scrolled through.	  
- m;searchteams [searchterm]
  - shows a paginated list of all teams whose names contain the given search term.
  
### player commands:	 
- m;showplayer [name]
  - displays any name's stars, there's a limit of 70 characters. that should be *plenty*. note: if you want to lookup a lot of different players you can do it on onomancer instead of spamming this command a bunch and clogging up discord: https://onomancer.sibr.dev/reflect
- m;idolize [name]
  - records any name as your idol, mostly for fun.
- m;showidol 
  - displays your idol's name and stars.
  
### game commands:
- m;startgame
  - starts a game with premade teams made using saveteam. use this command at the top of a list followed by each of these in a new line:
	- the away team's name.
	- the home team's name.
	- optionally, the number of innings, which must be greater than 2 and less than 31. if not included it will default to 9.	  

### other commands:
- m;help [command]
  - shows the instructions from here for given command. if no command is provided, it will instead provide a list of all of the commands that instructions can be provided for.    
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
