from ..messages import (AppendEntriesRequest, AppendEntriesSuccess,
                        ClientViewChangeRequest, CommitMessage, ElectedMessage,
                        SignedMessage, VoteMessage)
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
        self.server.timeout_manager.set_timeout(
            self.config.timeout / 2, ResendVoteTimeout(self.term))
        self.server.timeout_manager.set_timeout(
            self.config.timeout, GiveUpTimeout(self.term))

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

    def on_client_view_change_request(self, msg: ClientViewChangeRequest,
                                      signed: SignedMessage[ClientViewChangeRequest]) -> 'State':
        # ignore client view change requests; we will already increment view
        # if candidate is not successfully elected within a timeout
        return self

    def on_timeout(self, context: object):
        if isinstance(context, ResendVoteTimeout) and context.term == self.term:
            self.send_vote()
            return self
        elif isinstance(context, GiveUpTimeout) and context.term == self.term:
            self.config.double_timeout()
            return self.increment_term()
        else:
            return super(Voter, self).on_timeout(context)


class ResendVoteTimeout(object):
    def __init__(self, term: int) -> None:
        self.term = term


class GiveUpTimeout(object):
    def __init__(self, term: int) -> None:
        self.term = term
