from ..messages import (AppendEntriesRequest, AppendEntriesSuccess,
                        CommitMessage, ElectedMessage, SignedMessage,
                        VoteMessage)
from ..servers.base import BaseServer
from .state import State


class Voter(State):
    def __init__(self, term: int,
                 server: BaseServer,
                 copy_from: State) -> None:
        super(Voter, self).__init__(server, copy_from, term)

    def send_vote(self):
        vote = VoteMessage(self.config.server_id,
                           self.term, self.latest_a_cert)
        self.server.messenger.send_server_message(
            self.term % self.config.num_servers, vote)
        # TODO: set a timeout here

    def start(self):
        '''A server initially in the Voter state sends a vote to the primary.'''
        self.send_vote()

    def on_append_entries_request(self, msg: AppendEntriesRequest,
                                  signed: SignedMessage[AppendEntriesRequest]) -> 'State':
        if msg.term >= self.term:
            self._request_election_proof(msg.term)
        return self

    def on_append_entries_success(self, msg: AppendEntriesSuccess,
                                  signed: SignedMessage[AppendEntriesSuccess]) -> 'State':
        if msg.term >= self.term:
            self._request_election_proof(msg.term)
        return self

    def on_commit(self, msg: CommitMessage,
                  signed: SignedMessage[CommitMessage]) -> 'State':
        if msg.term >= self.term:
            self._request_election_proof(msg.term)
        return self

    def on_elected(self, msg: ElectedMessage,
                   signed: SignedMessage[ElectedMessage]) -> 'State':
        from .follower import Follower

        # Transition to follower state if election proof is for a future term.
        if msg.term < self.term:
            return self
        leader_commit_idx, commit_idx_a_cert = msg.leader_commit_idx()
        return Follower(msg.term, leader_commit_idx,
                        commit_idx_a_cert, self)
