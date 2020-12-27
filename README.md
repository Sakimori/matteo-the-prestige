# matteo-the-prestige
# simsim discord bot

blaseball, blaseball, is back! in an unofficial capacity.

custom players, custom teams, custom leagues (that last one is coming soon™) all in discord! 

we've also got things like player  idolization, easy setup for quick pick-up games featuring any players you like (including those not on a team), and onomancer lookup

accepting pull requests, check the issues for to-dos


## commands: (literally everything here is case sensitive, and can be prefixed with either m; or m!)

- team commands:
	- m;saveteam
	  - saves a team to the database allowing it to be used for games, send this command at the top of a list, with lines seperated by newlines (shift+enter in discord, or copy+paste from notepad)
		- the first line of the list is your team's name (cannot contain emoji)
		- the second is your team's slogan, this should begin with an emoji followed by a space
		- the next lines are your batters' names in the order you want them to appear in your lineup, minimum batters: 1, maximum batters: 12
		- the final line is your pitcher
	  - if you did it correctly, you'll get a team embed with a prompt to confirm. hit the 👍 and it'll be saved
	- m;showteam [name]
	  - shows information about any saved team	  
	- m;showallteams
	  - shows a paginated list of all teams available for games	  
	- m;searchteams [searchterm]
	  - displays paginated list of all teams whose names contain the given string

- player commands:	 
	- m;showplayer [name]
	  - displays any name's stars, there's a limit of 70 characters. that should be *plenty*
	- m;idolize [name]
	  - records any name as your idol, used elsewhere  	  
	- m;showidol 
	  - displays your idol's name and stars
  
- game commands:
	- m;startgame
	  - starts a game with premade teams, use this command at the top of a list followed by, each in a new line:
		- the away team's name
		- the home team's name
		- and finally, optionally, the number of innings, which must be greater than 2 and less than 31, if not included this will default to 9	  
	- m;setupgame
	  - begins setting up a 3-inning pickup game. pitchers, lineups, and team names are given during the setup process by anyone able to type in that channel. idols are easily signed up via emoji during the process. the game will start automatically after setup.

- other commands:    
	- m;credit
	  - shows artist credit for matteo's avatar
	  
	- m;roman [number]
	  - converts any natural number less than 4,000,000 into roman numerals, this one is just for fun
