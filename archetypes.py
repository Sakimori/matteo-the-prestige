import random
from gametext import appearance_outcomes
from discord.app_commands import Choice

class Archetype:
    name = "basic"
    display_name = "Jack of All Trades"
    display_symbol = "🃏"
    description = "Master of none. This archetype has no bonuses and no penalties."

    def modify_player_stats(player):
        """This is called once at the start of every game"""
        pass

    def modify_bat_rolls(outcome, rolls):
        """"modify the rolls used in batting before using the rolled values"""
        pass

    def modify_out_type(outcome):
        """if the batter would go out, do something"""
        pass

    def modify_hit_type(outcome):
        """if the batter would get a hit, do something"""
        pass

    def hold_runner(outcome, stats):
        """affect the pitcher's ability to prevent steal attempts"""
        pass

    def steal_check(outcome, steal_roll):
        """make a runner more or less likely to steal"""
        pass

    def modify_steal_attempt(outcome, steal_success_roll):
        """affect a runner's ability to successfully steal"""
        pass

    def modify_tag_up_roll(outcome, run_roll):
        """change the runner's decision to tag-up"""
        pass

    def modify_advance_roll(outcome, run_roll):
        """change the runner's decision to advance on groundouts"""
        pass

    def modify_extra_running_roll(outcome, run_roll):
        """change the runner's ability to advance extra bases on base hits by a teammate"""
        pass

class ThreeTrueOutcomes(Archetype):
    name = "pure power"
    display_name = "Three True Outcomes"
    description = "There are three outcomes in baseball that do not involve the batter running to first. Strikeouts, walks, and home runs. You'll get lots of these."

    def modify_out_type(outcome): #if the batter flies out or grounds out, change 60% to a strikeout
        if outcome["outcome"] in [appearance_outcomes.groundout, appearance_outcomes.flyout] and random.random() > 0.4:
            outcome["outcome"] = appearance_outcomes.strikeoutswinging

    def modify_hit_type(outcome): #if the batter gets a double, 50% chance for home run instead. Singles become strikeouts or home runs often.
        roll = random.random()
        if outcome["outcome"] in [appearance_outcomes.double, appearance_outcomes.triple] or roll > 0.8:
            outcome["outcome"] = appearance_outcomes.homerun
        elif outcome["outcome"] == appearance_outcomes.single and roll < 0.4:
            outcome["ishit"] = False
            outcome["outcome"] = appearance_outcomes.strikeoutswinging

class ContactHitter(Archetype):
    name = "contact"
    display_name = "Contact Specialist"
    description = "Some folks know how to get on base. Other folks learn from them. Unfortunately, these techniques make power more difficult to find."

    def modify_bat_rolls(outcome, rolls): #if it's not a hit *and* not a walk, maybe get a hit anyway. Always reduce power.
        rolls["hitnum"] = rolls["hitnum"] * 0.75
        if rolls["pb_system_stat"] <= 0 and rolls["hitnum"] < 4 and random.random() > 0.8:
            rolls["pb_system_stat"] = 0.5
            rolls["hitnum"] = rolls["hitnum"] * 0.5

class Sprinter(Archetype):
    name = "speed"
    display_name = "Sprinter"
    description = "Speed can make up for a lack of strength in a lot of ways. Baserunning and defensive ability increase, at the expense of home run power."

    def modify_player_stats(player):
        player.stlats["baserunning_stars"] = player.stlats["baserunning_stars"] + 2
        player.stlats["defense_stars"] = player.stlats["defense_stars"] + 2
        
    def modify_bat_rolls(outcome, rolls): #reduce power
        rolls["hitnum"] = rolls["hitnum"] * 0.8

class Stuff(Archetype):
    name = "velocity"
    display_name = "They've Got the Stuff"
    description = "'Stuff' is one of the ways to talk about how fast a pitcher can throw the ball. This player has *got the stuff,* but it's hard to aim when you're throwing that fast. Watch for outs and walks to increse."

    def modify_bat_rolls(outcome, rolls):
        if random.random() > 0.9:
            rolls["pb_system_stat"] = -1

        if rolls["pb_system_stat"] <= 0:
            if rolls["hitnum"] > 3: #expand the Walk Zone
                rolls["hitnum"] = 4.5
            elif rolls["hitnum"] < 0: #expand the Strikeout Zone
                rolls["hitnum"] = -2

class Control(Archetype):
    name = "control"
    display_name = "Puppetmaster"
    description = "A pitcher with control knows how to 'pull the string' on a pitch well after it's been thrown. Batters are going to be swinging out of their shoes, but you're going to get more contact than usual. Weak contact, but still."

    def modify_bat_rolls(outcome, rolls):
        if random.random() > 0.75:
            rolls["hitnum"] = rolls["hitnum"] * 0.5
        else:
            rolls["hitnum"] = rolls["hitnum"] * 0.9

        if random.random() < 0.1:
            rolls["pb_system_stat"] = 1        

def all_archetypes():
    return [
        Archetype,
        ThreeTrueOutcomes,
        ContactHitter,
        Sprinter,
        Stuff,
        Control
        ]

def archetype_choices():
    lst = []
    for arch in all_archetypes():
        lst.append(Choice(name=arch.display_name, value=arch.name))
    return lst

def search_archetypes(text):
    for archetype in all_archetypes():
        if archetype.name == text or archetype.display_name.lower() == text.lower():
            return archetype
    return None