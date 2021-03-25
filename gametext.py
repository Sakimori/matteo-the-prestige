from enum import Enum

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
        self.intro_counter = 1
        self.post_format = []

    default_format = ("defender",)

    intro_formats = []
    intro = [("🎆", "Play ball!")]

    strikeoutlooking = ["strikes out looking."]
    strikeoutswinging = ["strikes out swinging."]
    groundout = ["grounds out to {}."]
    flyout = ["flies out to {}."]
    fielderschoice = ["reaches on fielder's choice. {} is out at {} base."] #requires .format(player, base_string)
    doubleplay = ["grounds into a double play!"]
    sacrifice = ["hits a sacrifice fly towards {}."]
    walk = ["draws a walk."]
    single = ["hits a single!"]
    double = ["hits a double!"]
    triple = ["hits a triple!"]
    homerun = ["hits a dinger!"]
    grandslam = ["hits a grand slam!"]

    twoparts = []

    diff_formats = {fielderschoice[0]: ("defender", "base_string")}
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

class TheGoddesses(game_strings_base):

    def __init__(self):
        self.intro_counter = 4
        self.post_format = []

    intro = [("💜", "This game is now blessed 💜"), ("🏳️‍⚧️","I'm Sakimori,"), ("🌺", "and i'm xvi! the sim16 goddesses are live and on-site, bringing you today's game."), ("🎆", "Get hyped!!")]

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
              ("hits a shallow fly to short center field, this might get down for a base hit...", "{} dives forward and catches it! We love to see it, 16.")]

    fielderschoice = ["hits a soft grounder to shortstop, and {} forces {} out the short way. {} reaches on fielder's choice this time.",
                      "sharply grounds to third, and the throw over to {} forces {} out with a fielder's choice."]

    doubleplay = ["grounds to {}. the throw to second makes it in time, as does the throw to first! {} turn the double play!",
                  "hits a grounder tailor-made for a double play right to {}. Two quick throws, and {} do indeed turn two!"]

    sacrifice = [("hits a deep fly ball to right field, and {} looks ready to tag up...", "They beat the throw by a mile!"),
                 "sends a fly ball to deep center field, and {} comfortably tags up after the catch."]

    walk = ["watches a changeup miss low, and takes first base for free.",
            "is given a walk after a slider misses the zone for ball iv.",
            ("takes a close pitch that just misses inside, and is awarded a base on balls.", "saki. did you really just call it that? in [current year]?"),
            "is walked on iv pitches.",
            "jumps away from the plate as ball 4 misses far inside, just avoiding the hit-by-pitch and taking first on a walk."]

    single = [("tries to sneak a grounder between third base and the shortstop, but it's stopped by {} with a dive! They throw to first from their knees...", "but they beat the throw! {} is safe at first with a hit."),
              "hits a soft line drive over the infield, and makes it to first as it lands in the grass for a single.",
              "shoots a comebacker right over second base and pulls into first safely, racking up a base hit."]

    double = ["hits a double!"]
    triple = ["hits a triple!"]
    homerun = ["hits a dinger!"]
    grandslam = ["hits a grand slam!"]

    diff_formats = {groundout[3][1] : ("batter",),
               flyout[0][1]: ("batter",), flyout[2][1]: ("defender", "batter"),
               fielderschoice[0]: ("defender", "fc_out", "batter"), fielderschoice[1]: ("base_string", "fc_out"),
               doubleplay[0]: ("defender", "defense_team"), doubleplay[1]: ("defender", "defense_team"),
               sacrifice[0][0]: ("runner",), sacrifice[1]: ("runner",),
               single[0][1]: ("batter",)}
    no_formats = strikeoutlooking + strikeoutswinging + walk + single[1:] + [flyout[4][0], sacrifice[0][1]]
    twoparts = [groundout[1], groundout[3], flyout[0], flyout[2], flyout[4], walk[2], single[0], sacrifice[0]]




def base_string(base):
    if base == 1:
        return "first"
    elif base == 2:
        return "second"
    elif base == 3:
        return "third"
    elif base == 4:
        return "None"

