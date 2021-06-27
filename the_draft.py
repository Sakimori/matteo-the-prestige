from collections import namedtuple
import games
import json
import uuid
import real_players
import onomancer

Participant = namedtuple('Participant', ['handle', 'team'])
BOOKMARK = Participant(handle="bookmark", team=None)  # keep track of start/end of draft round


class Draft:
    """
    Represents a draft party with n participants constructing their team from a pool
    of names.
    """

    @classmethod
    def make_draft(cls, teamsize, draftsize, minsize, pitchers, ono_ratio):
        draft = cls(teamsize, draftsize, minsize, pitchers, ono_ratio)
        return draft

    def __init__(self, teamsize, draftsize, minsize, pitchers, ono_ratio):     
        self.DRAFT_SIZE = int(draftsize * ono_ratio)
        self.REAL_SIZE = draftsize - self.DRAFT_SIZE
        self.REFRESH_DRAFT_SIZE = minsize  # fewer players remaining than this and the list refreshes
        self.DRAFT_ROUNDS = teamsize
        self.pitchers = pitchers
        self._id = str(uuid.uuid4())[:6]
        self._participants = []
        self._active_participant = BOOKMARK  # draft mutex
        nameslist = onomancer.get_names(limit=self.DRAFT_SIZE)
        nameslist.update(real_players.get_real_players(self.REAL_SIZE))
        self._players = nameslist
        self._round = 0

    @property
    def round(self):
        """
        Current draft round. 1 indexed.
        """
        return self._round

    @property
    def active_drafter(self):
        """
        Handle of whomever is currently up to draft.
        """
        return self._active_participant.handle

    @property
    def active_drafting_team(self):
        return self._active_participant.team.name

    def add_participant(self, handle, team_name, slogan):
        """
        A participant is someone participating in this draft. Initializes an empty team for them
        in memory.

        `handle`: discord @ handle, for ownership and identification
        """
        team = games.team()
        team.name = team_name
        team.slogan = slogan
        self._participants.append(Participant(handle=handle, team=team))

    def start_draft(self):
        """
        Call after adding all participants and confirming they're good to go.
        """
        self.advance_draft()

    def refresh_players(self):
        nameslist = onomancer.get_names(limit=self.DRAFT_SIZE)
        nameslist.update(real_players.get_real_players(self.REAL_SIZE))
        self._players = nameslist

    def advance_draft(self):
        """
        The participant list is treated as a circular queue with the head being popped off
        to act as the draftign mutex.
        """
        if self._active_participant == BOOKMARK:
            self._round += 1
        self._participants.append(self._active_participant)
        self._active_participant = self._participants.pop(0)

    def get_draftees(self):
        return list(self._players.keys())

    def draft_player(self, handle, player_name):
        """
        `handle` is the participant's discord handle.
        """
        if self._active_participant.handle != handle:
            raise ValueError(f'{self._active_participant.handle} is drafting, not you')

        player_name = player_name.strip()

        player = self._players.get(player_name)
        if not player:
            # might be some whitespace shenanigans
            for name, stats in self._players.items():
                if name.replace('\xa0', ' ').strip().lower() == player_name.lower():
                    player = stats
                    break
            else:
                # still not found
                raise ValueError(f'Player `{player_name}` not in draft list')
        del self._players[player['name']]

        if len(self._players) <= self.REFRESH_DRAFT_SIZE:
            self.refresh_players()

        if self._round <= self.DRAFT_ROUNDS - self.pitchers:
            self._active_participant.team.add_lineup(games.player(json.dumps(player)))
        else:
            self._active_participant.team.add_pitcher(games.player(json.dumps(player)))

        self.advance_draft()
        if self._active_participant == BOOKMARK:
            self.advance_draft()

        return player

    def get_teams(self):
        teams = []
        if self._active_participant != BOOKMARK:
            teams.append((self._active_participant.handle, self._active_participant.team))
        for participant in self._participants:
            if participant != BOOKMARK:
                teams.append((participant.handle, participant.team))
        return teams

    def finish_draft(self):
        for handle, team in self.get_teams():
            success = games.save_team(team, int(handle[3:-1]))
            if not success:
                raise Exception(f'Error saving team for {handle}')


if __name__ == '__main__':
    # extremely robust testing OC do not steal
    DRAFT_ROUNDS = 2
    draft = Draft.make_draft()
    draft.add_participant('@bluh', 'Bluhstein Bluhs', 'bluh bluh bluh')
    draft.add_participant('@what', 'Barcelona IDK', 'huh')
    draft.start_draft()

    while draft.round <= DRAFT_ROUNDS:
        print(draft.get_draftees())
        cmd = input(f'{draft.round} {draft.active_drafter}:')
        drafter, player = cmd.split(' ', 1)
        try:
            draft.draft_player(drafter, player)
        except ValueError as e:
            print(e)
    print(draft.get_teams())
