# matteo-the-prestige
# simsim discord bot

blaseball, blaseball, is back! in an unofficial capacity.

custom players, custom teams, custom leagues (that last one is coming soon™) all in discord! 



we've also got things like player  idolization, easy setup for quick pick-up games featuring any players you like (including those not on a team), and onomancer lookup

accepting pull requests, check the issues for to-dos

## commands: (literally everything here is case sensitive, and can be prefixed with either m; or m!)

- m;idolize [name]
  - records any name as your idol, used elsewhere. there's a limit of 70 characters. that should be *plenty*. 
  
- m;showidol 
  - displays your idol's name and stars in a nice discord embed.
  
- m;showplayer [name]
  - displays any name's stars in a similar embed.
  
- m;setupgame
  - begins setting up a 3-inning pickup game. pitchers, lineups, and team names are given during the setup process by anyone able to type in that channel. idols are easily signed up via emoji during the process. the game will start automatically after setup.
  
- m;saveteam
  - to save an entire team, send this command at the top of a list, with lines seperated by newlines (shift+enter in discord, or copy+paste from notepad)
    - the first line of the list is your team's name (cannot contain emoji)
    - the second is your team's slogan
    - the rest of the lines are your players' names
    - the last player is designated your pitcher
  - if you did it correctly, you'll get a team embed with a prompt to confirm. hit the 👍 and it'll be saved.

- m;showteam [name]
  - you can view any saved team with this command

- m;startgame
  - to start a game with premade teams, use this command at the top of a list as above
    - the first line is the away team's name
    - the second is the home team's name
    - the third is the number of innings, which must be greater than 2.
    
- m;credit
  - shows artist credit for matteo's avatar.
  
- m;roman [number]
  - converts any natural number less than 4,000,000 into roman numerals. this one is just for fun.
