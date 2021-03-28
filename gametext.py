from enum import Enum
from random import randrange

class appearance_outcomes(Enum):
    strikeoutlooking = "strikes out looking."
    strikeoutswinging = "strikes out swinging."
    groundout = "grounds out to"
    flyout = "flies out to"
    fielderschoice = "reaches on fielder's choice. {} is out at {} base." #requires .format(player, base_string)
    doubleplay = "grounds into a double play!"
    sacrifice = "hits a sacrifice fly towards"
    walk = "draws a walk."
    single = "hits a single!"
    double = "hits a double!"
    triple = "hits a triple!"
    homerun = "hits a dinger!"
    grandslam = "hits a grand slam!"

class game_strings_base(object):
    def __init__(self):
        self.intro_counter = 2
        self.post_format = []

    default_format = ("defender",)

    intro_formats = []
    intro = [("⚡","Automated Baseball Caster V16.38, now online."),("⚡", "Play ball!")]

    strikeoutlooking = ["strikes out looking."]
    strikeoutswinging = ["strikes out swinging."]
    groundout = ["grounds out to {}."]
    flyout = ["flies out to {}."]
    fielderschoice = ["reaches on fielder's choice. {} is out at {} base."] 
    doubleplay = ["grounds into a double play!"]
    sacrifice = ["hits a sacrifice fly towards {}."]
    walk = ["draws a walk."]
    single = ["hits a single!"]
    double = ["hits a double!"]
    triple = ["hits a triple!"]
    homerun = ["hits a dinger!"]
    grandslam = ["hits a grand slam!"]

    steal_caught = ["{} was caught stealing {} base by {}!"]
    steal_success = ["{} steals {} base!"]

    twoparts = []

    diff_formats = {fielderschoice[0]: ("defender", "base_string"),
                    steal_success[0]: ("runner", "base_string"),
                    steal_caught[0]: ("runner", "base_string", "defender")}
    no_formats = strikeoutlooking + strikeoutswinging + doubleplay + walk + single + double + triple + homerun + grandslam

    def activate(self, lastupdate, currentupdate, game):
        if "twopart" in lastupdate:
            for key, value in lastupdate.items():
                if key != "twopart":
                    currentupdate[key] = value
            currentupdate["displaytext"] = self.format_gamestring(getattr(self, currentupdate["outcome"].name)[currentupdate["voiceindex"]][1], currentupdate)

        elif "outcome" in currentupdate:
            if self.check_for_twopart(getattr(self, currentupdate["outcome"].name)[currentupdate["voiceindex"]]):
                currentupdate.update({
                    "twopart": True,
                    "displaytext": f"{currentupdate['batter']} {self.format_gamestring(getattr(self, currentupdate['outcome'].name)[currentupdate['voiceindex']][0], currentupdate)}"
                    })
            else:
                currentupdate["displaytext"] = f"{currentupdate['batter']} {self.format_gamestring(getattr(self, currentupdate['outcome'].name)[currentupdate['voiceindex']], currentupdate)}"

    def check_for_twopart(self, gamestring): 
        return gamestring in self.twoparts

    def format_gamestring(self, gamestring, update):
        if gamestring in self.no_formats:
            return gamestring
        elif gamestring in self.diff_formats:
            return gamestring.format(*self.parse_formats(self.diff_formats[gamestring], update))
        else:
            return gamestring.format(*self.parse_formats(self.default_format, update))

    def parse_formats(self, format_tuple, update):
        out_list = []
        for string in format_tuple:
            if string == "defender":
                out_list.append(update['defender'].name)
            elif string == "base_string":
                self.post_format.append("base")
                out_list.append("{}")
            elif string == "batter":
                out_list.append(update['batter'].name)
            elif string == "fc_out" or string == "runner":
                self.post_format.append("runner")
                out_list.append("{}")
            elif string == "defense_team":
                out_list.append(update['defense_team'].name)
            elif string == "offense_team":
                out_list.append(update['offense_team'].name)
        return tuple(out_list)

    def activate_weather(self, lastupdate, currentupdate, game):
        pass

    def stealing(self, currentupdate, runner, base_string, defender, is_successful):
        if is_successful:
            index = randrange(0, len(self.steal_success))
            text = self.steal_success[index]
        else:
            index = randrange(0, len(self.steal_caught))
            text = self.steal_caught[index]

        if text not in self.no_formats:
            format_list = []
            for format in self.diff_formats[text]:
                if format == "runner":
                    format_list.append(runner)
                elif format == "base_string":
                    format_list.append(base_string)
                elif format == "defender":
                    format_list.append(defender)

        currentupdate["steals"] = [text.format(*format_list)]

class TheGoddesses(game_strings_base):

    def __init__(self):
        self.intro_counter = 4
        self.post_format = []

    intro = [("💜", "This game is now blessed 💜"), ("🏳️‍⚧️","I'm Sakimori,"), ("🌺", "and i'm xvi! the sim16 goddesses are live and on-site, bringing you today's game."), ("🎆", "It's time to play ball!!")]

    strikeoutlooking = ["watches a slider barely catch the outside corner. Hang up a ꓘ!", 
                        "looks at a fastball paint the inside of the plate, and strikes out looking.", 
                        "can't believe it as the ump calls strike 3 on a pitch that could have gone either way!",
                        "freezes up as a curveball catches the bottom edge of the zone. strike iii!"]

    strikeoutswinging = ["swings at a changeup in the dirt for strike 3!",
                         "can't catch up to the fastball, and misses strike iii.",
                         "just misses the cutter and strikes out with a huge swing."]

    groundout = ["hits a sharp grounder to {}! they throw to first and get the out easily.",
                 ("tries to sneak a grounder between third base and the shortstop, but it's stopped by {} with a dive! They throw to first from their knees...", "and force the groundout!"),
                 "hits a routine ground ball to {} and is put out at first.",
                 ("pulls a swinging bunt to {}, who rushes forward and throws to first...", "in time! {} is out!")]

    flyout = [("shoots a line drive over {}'s head...", "They leap up and catch it! {} is out!!"),
              "is out on a routine fly ball to {}.",
              ("hits a high fly ball deep to center! this one looks like a dinger...", "{} jumps up and steals it! {} is out!"),
              "lines a ball to first, and it's caught by {} for the easy out.",
              ("hits a shallow fly to short center field! this might get down for a base hit...", "{} dives forward and catches it! We love to see it, 16.")]

    fielderschoice = ["hits a soft grounder to shortstop, and {} forces {} out the short way. {} reaches on fielder's choice this time.",
                      "sharply grounds to third, and the throw over to {} forces {} out with a fielder's choice."]

    doubleplay = ["grounds to {}. the throw to second makes it in time, as does the throw to first! {} turn the double play!",
                  ("hits a grounder tailor-made for a double play right to {}.", "Two quick throws, and {} do indeed turn two!")]

    sacrifice = [("hits a deep fly ball to right field, and {} looks ready to tag up...", "They beat the throw by a mile!"),
                 "sends a fly ball to deep center field, and {} comfortably tags up after the catch."]

    walk = ["watches a changeup miss low, and takes first base for free.",
            "is given a walk after a slider misses the zone for ball iv.",
            ("takes a close pitch that just misses inside, and is awarded a base on balls.", "saki. did you really just call it that? in [current year]?"),
            "is walked on iv pitches.",
            "jumps away from the plate as ball 4 misses far inside, just avoiding the hit-by-pitch and taking first on a walk."]

    single = [("tries to sneak a grounder between third base and the shortstop, but it's stopped by {} with a dive! They throw to first from their knees...", "but they beat the throw! {} is safe at first with a hit."),
              ("shoots a line drive over {}'s head...", "They leap up but can't quite reach it! {} is safe at first with a single!!"),
              ("pulls a swinging bunt to {}, who rushes forward and throws to first...", "{} tags the bag just before the throw, and are rewarded with an infield single!"),
              "hits a soft line drive over the infield, and makes it to first as it lands in the grass for a single.",
              "shoots a comebacker right over second base and pulls into first safely, racking up a base hit.",
              "hits a hard grounder into the right-side gap for a base hit."]

    double = [("hits a shallow fly to short center field! this might get down for a base hit...", "{} dives for it, but can't quite get there! {} makes it around to second before the ball gets chased down. Good effort though!"),
              "hits a fly ball into the outfield gap and pulls into second with a stand-up double.",
              ("hits a high fly ball deep to center! this one looks like a dinger...", "hell. it bounces off the wall, and that's a double."),
              "shoots a line drive right down the third base line, just getting past {} for a double!"]

    triple = ["hits a fly ball down the first base line! it lands fair, and gives {} enough time to round the bases all the way to third!!",
              "stretches a line drive to the outfield gap from a double to a triple with a dive into third, just beating the throw!"]

    homerun = [("hits a high fly ball deep to center! this one looks like a dinger...", "{} jumps up for the steal but can't get to it! Rack up another dinger for {}!"),
               ("hits a no-doubter over the right field wall!","Artemis won't be happy about that one 😅"),
               "smacks a dinger to right field and takes a free trip around the basepaths.",
               "hits a fly ball to deep left field, and it barely gets over the wall for a dinger!"]

    grandslam = ["hits a fly ball to deep left field, and it barely gets over the wall for a GRAND SLAM!!!",
                 ("hits a high fly ball deep to center! this one looks like a dinger...", "{} jumps up for the steal but can't get to it! {} gets a grand slam!!!")]

    steal_success = ["{} takes {} with ease on a low changeup!",
                     "{} steals {} after a close throw from {} is just a moment too late!",
                     "{} tries to catch {} stealing, but a high throw means they pull off the steal at {} just in time."]

    steal_caught = ["{} catches {} trying to steal {} with a laser throw!",
                    "{} tries to steal {}, but they can't beat the throw and get caught.",
                    "{} gets caught stealing easily with that throw from {}!"]

    diff_formats = {groundout[3][1] : ("batter",),
               flyout[0][1]: ("batter",), flyout[2][1]: ("defender", "batter"),
               fielderschoice[0]: ("defender", "fc_out", "batter"), fielderschoice[1]: ("base_string", "fc_out"),
               doubleplay[0]: ("defender", "defense_team"), doubleplay[1][1]: ("defense_team",),
               sacrifice[0][0]: ("runner",), sacrifice[1]: ("runner",),
               single[0][1]: ("batter",), single[1][1]: ("batter",), single[2][1]: ("batter",),
               double[0][1]: ("defender", "batter"),
               triple[0]: ("batter",),
               homerun[0][1]: ("defender", "batter"),
               grandslam[1][1]: ("defender", "batter"),
               steal_success[0]: ("runner", "base_string"), steal_success[1]: ("runner", "base_string", "defender"), steal_success[2]: ("defender", "runner", "base_string"),
               steal_caught[0]: ("defender", "runner", "base_string"), steal_caught[1]: ("runner", "base_string"), steal_caught[2]: ("runner", "defender")}

    no_formats = strikeoutlooking + strikeoutswinging + walk + single[3:] + [flyout[4][0], sacrifice[0][1], 
                                                                             double[0][0], double[1], double[2][0], double[2][1], triple[1],
                                                                             homerun[0][0], homerun[1][0], homerun[1][1], homerun[2:],
                                                                             grandslam[0], grandslam[1][0]]

    twoparts = [groundout[1], groundout[3], flyout[0], flyout[2], flyout[4], walk[2], doubleplay[1], single[0], single[1], single[2], sacrifice[0], double[0], double[2], homerun[0], homerun[1], grandslam[1]]

class TheNewGuy(game_strings_base):
    def __init__(self):
        self.intro_counter = 4
        self.post_format = []

    intro = [("👋","Hey, folks! First day, great to be here."),("👋", "Never played Baseball, or, uh, seen it, but I’m really excited to learn along with you."),("👋", "Here we go! Uh, how’s it go again…"),("👋", "Play baseball!")]

    strikeoutlooking = ["watches the ball go right past ‘em. Think you’re supposed to hit it. And they’re out.",
                        "waits for the bat to start moving on its own, I guess? It doesn’t, so… they’re out.",
                        "doesn’t even try to go for the ball, apparently, and they’re out."]

    strikeoutswinging = ["swings, but the ball is already past them! They were off by a mile! They’re out.",
                         "swings three times, but never actually hits the ball. Out!",
                         "swings three times, and it looks like they’re headed home! I-in a bad way. As in they’re out."]

    groundout = ["hits the ball! It rolls over to {}, who’s throwing it to first, and… yep. That’s an out, I guess.",
                 "hits the ball! Nice!! And there they go, running towards first! Wait, since when did {} have the ball— and, whoops, yeah, they’re out at first.",
                 "hits the ball right onto the ground. It rolls over to {}, who nabs it and tosses it to first, and it looks like {}’s out.",
                 "hits the ball over to the right side of the field. And it looks like {}’s sending it right over to first, where {}’s out."]

    flyout = [("knocks the ball real hard right over {}.","They leap up and catch it! {} is out!!"),
              "hits the ball super high up in the air! But it drops right into the hands of {}.",
              ("absolutely SMASHES that ball! It’s gone!","Woah, hold on, nevermind. It looks like {} jumped up and grabbed it!"),
              "bops the ball up in the air and over to {}. Worth a go, I guess?",
              ("winds up a real heavy hit, and the ball goes really fast!", "Not fast enough to faze {}, though, who does a spectacular leap over and nabs it out of the air.")]

    fielderschoice = ["whacks the ball over to the left side of the baseball triangle, where {} sends {} back to their pit. {}’s on base, though!",
                      ("hits the ball onto the ground, where it rolls over to the second-and-a-half-base guard.","That guard puts a stop to {}’s running, but they forgot about {}!")]

    doubleplay = [("hits the ball over to {}, who picks it up and stops that runner at second.", "And they’re not done! They toss it to first and get {} out, too. Yikes."),
                  "hits the ball to {}, who gets that runner from first out before tossing it right back at first, and… wow. That went as poorly as it could’ve. They’re both out."]

    sacrifice = [("does a little mini-hit, bumping the ball onto the field. {}’s got it, and, yeah, they’re out at first.", "Wait, when did {} score? Oh, was that— that was clever! Very nice."),
                 "POUNDS the ball right up into the air! It lands right in the hands of {}, but {} takes the opportunity to stroll over to the one that gives points!"]

    walk = ["watches the ball go right past them four times, and… gets to advance? Okay!",
            ("just stands there. The umpire’s calling it a ball, which… they’re all balls, aren’t they? It’s baseball, not—", "Oh, uh, right. They’re on first now. I guess."),
            "hangs out for four throws, gets bored, and walks over to first. Didn’t know you can do that, but good for them!", 
            "gets smacked with the ball! Yikes! They’re limping over to first, so… we’re… we’re just going to keep going, then. Alright!"]

    single = [("knocks the ball real hard right over {}.", "And get away with it, too, making it to first long before the ball does!"),
              "hits the ball too hard for anyone to nab it and runs right over to first.",
              "barely brushes up against the ball with the bat, and it lands pretty close to them. A bunch of folks scramble for it, but not before {} makes it to first!"]

    double = ["hits the ball super hard, and while everyone’s scrambling for it they’re off to first! No, second!!",
              "whacks the ball and gets out of there, making it to first and then second before anyone on the field can get the ball near them."]

    triple = ["obliterates the ball and gets moving! They’re at first! No, second! No, they’re at third! And... Oh, that’s it, they’re done. Okay.",
              "hits a three-base baseball whack! They try to go a little extra, but get scared into running back to third. Works."]

    homerun = ["whacks the ball out of the park!! The crowd’s going wild as they run all the way around the baseball triangle and back to zeroth base!",
              ("absolutely SMASHES that ball! It’s gone!", "And so are they, as they run all the bases and head right back home!"),
              "hits a home run! Ooh, I know this one!"]

    grandslam = ["hits the ball and chases all their friends home with them!",
                  "whacks the ball onto the ground reeeally far away. {} gets to it eventually, but not in time to stop ANYONE from making it home!!",
                  "hits a quadruple home run!"]

    steal_success = ["runs to the next base too early!! You can do that??",
                    "is cheating!! They just ran to the next base and nobody even hit the ball!",
                    "gets bored of waiting and takes off, narrowly making it to the next base!"]

    steal_caught = ["tries to run to the next base too early, and gets caught cheating!",
                    "sees if they can get away with dashing over to the next base. They can’t, turns out.",
                    "tries running to the next base, but {}’s ready for them. Out!"]

    no_formats = strikeoutlooking + strikeoutswinging + walk + double + triple + steal_success + steal_caught[:2] + [flyout[2][0], flyout[4][0], fielderschoice[1][0], single[0][1], single[1], walk[1][0], walk[1][1],
                                                                                                                    homerun[0], homerun[1][0], homerun[1][1], homerun[2], grandslam[0], grandslam[2]]

    diff_formats = {groundout[2]: ("defender", "batter"), groundout[3]: ("defender", "batter"),
                    flyout[0][1]: ("batter",),
                    fielderschoice[0]: ("defender", "fc_out", "batter"), fielderschoice[1][1]: ("fc_out", "batter"),
                    doubleplay[0][1]: ("batter",),
                    sacrifice[0][1]: ("runner",), sacrifice[1]: ("defender", "runner"),
                    single[2]: ("batter",),
                    steal_caught[2]: ("defender",)}

    twoparts = [flyout[0], flyout[2], flyout[4], fielderschoice[1], doubleplay[0], sacrifice[0], walk[1], single[0], homerun[1]]



def all_voices():
    return {"default": game_strings_base,
        "The Goddesses": TheGoddesses,
        "The New Guy": TheNewGuy}


def base_string(base):
    if base == 1:
        return "first"
    elif base == 2:
        return "second"
    elif base == 3:
        return "third"
    elif base == 4:
        return "None"

