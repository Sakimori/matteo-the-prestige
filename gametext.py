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

def base_string(base):
    if base == 1:
        return "first"
    elif base == 2:
        return "second"
    elif base == 3:
        return "third"
    elif base == 4:
        return "None"

