import random
from gametext import appearance_outcomes

class Archetype:
    name = "basic"
    display_name = "Jack of All Trades"
    display_symbol = "🃏"

    def modify_bat_rolls(self, outcome, rolls):
        """"modify the rolls used in batting before using the rolled values"""
        pass

    def modify_out_type(self, outcome):
        """if the batter would go out, do something"""
        pass

    def modify_hit_type(self, outcome):
        """if the batter would get a hit, do something"""
        pass

    def hold_runner(self, outcome, stats):
        """affect the pitcher's ability to prevent steal attempts"""
        pass

    def steal_check(self, outcome, steal_roll):
        """make a runner more or less likely to steal"""
        pass