from collections import namedtuple
import games
import uuid

import onomancer

DRAFT_SIZE = 20
REFRESH_DRAFT_SIZE = 4  # fewer players remaining than this and the list refreshes
DRAFT_ROUNDS = 13

Participant = namedtuple('Participant', ['handle', 'team'])
BOOKMARK = Participant(handle="bookmark", team=None)  # keep track of start/end of draft round


class Draft:
    """
    Represents a draft party with n participants constructing their team from a pool
    of names.
    """

    _ongoing_drafts = {}

    @classmethod
    def make_draft(cls):
        draft = cls()
        cls._ongoing_drafts[draft._id] = draft
        return draft

    def __init__(self):
        self._id = str(uuid.uuid4())[:6]
        self._participants = []
        self._active_participant = BOOKMARK  # draft mutex
        self._players = onomancer.get_names(limit=DRAFT_SIZE)
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
        self._players = onomancer.get_names(limit=DRAFT_SIZE)

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
            raise ValueError('Invalid drafter')

        player_name = player_name.strip()

        player = self._players.get(player_name)
        if not player:
            # might be some whitespace shenanigans
            for name, stats in self._players.items():
                if name.replace('\xa0', ' ').strip() == player_name:
                    player = stats
                    break
            else:
                # still not found
                raise ValueError('Player not in draft list')
        del self._players[player['name']]

        if len(self._players) <= REFRESH_DRAFT_SIZE:
            self.refresh_players()

        if self._round < DRAFT_ROUNDS:
            self._active_participant.team.add_lineup(player['name'])
        elif self._round == DRAFT_ROUNDS:
            self._active_participant.team.set_pitcher(player['name'])

        self.advance_draft()
        if self._active_participant == BOOKMARK:
            self.advance_draft()

        return player

    def get_teams(self):
        teams = {}
        if self._active_participant != BOOKMARK:
            teams[self._active_participant.handle] = self._active_participant.team
        for participant in self._participants:
            if participant != BOOKMARK:
                teams[participant.handle] = participant.team
        return teams


if __name__ == '__main__':
    # extremely robust testing OC do not steal
    DRAFT_ROUNDS = 3
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
    print(draft.get_teams()['@bluh'].lineup)
    print(draft.get_teams()['@bluh'].pitcher)
    print(draft.get_teams()['@what'].lineup)
    print(draft.get_teams()['@what'].pitcher)
