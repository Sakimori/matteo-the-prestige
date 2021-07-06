import random
from gametext import appearance_outcomes

class Archetype:
    name = "basic"
    display_name = "Jack of All Trades"
    display_symbol = "🃏"
    description= "Master of none. This archetype has no bonuses and no penalties."

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

def all_archetypes():
    return [
        Archetype
        ]

def search_archetypes(text):
    for archetype in all_archetypes():
        if archetype.name == text or archetype.display_name == text:
            return archetype
    return None