import time, asyncio, jsonpickle
import database as db





class league(object):
    def __init__(self, name, subleagues_dic):
        self.subleagues = {} #key: name, value: [divisions]
        self.max_days
        self.day = 1
        self.name = name
        self.subleagues = subleagues_dic

class division(object):
    def __init__(self):
        self.teams = {} #key: team name, value: {wins; losses; run diff}

