from typing import Dict

from ..messages import ElectedMessage, SignedMessage, VoteMessage, VoteRequest
from ..servers.base import BaseServer
from .state import State


class Candidate(State):
    def __init__(self, term: int, votes_for_term: Dict[int, SignedMessage[VoteMessage]],
                 server: BaseServer, copy_from: State) -> None:
        super(Candidate, self).__init__(server, copy_from, term)

        # Add a vote from ourself
        self.votes_for_term = votes_for_term
        my_vote = VoteMessage(self.config.server_id, self.term, self.latest_a_cert)
        signed_my_vote = SignedMessage(my_vote, self.config.private_key)
        self.votes_for_term[self.config.server_id] = signed_my_vote

        # Should always transition here before having a quorum of votes
        assert len(self.votes_for_term) < self.config.quorum_size

    def send_vote_request(self):
        assert len(self.votes_for_term) >= self.config.f + 1
        req = VoteRequest(self.config.server_id, self.term,
                          list(self.votes_for_term.values()))
        self.server.messenger.broadcast_server_message(req)
        # TODO set a timeout here

    def on_vote(self, msg: VoteMessage,
                signed: SignedMessage[VoteMessage]) -> State:
        from .pre_leader import PreLeader
        print('Candidate.on_vote called')

        # Only handle votes for the current term, else revert to default behavior
        if msg.term != self.term:
            return super(Candidate, self).on_vote(msg, signed)

        self.votes_for_term[msg.sender_id] = signed
        proof = ElectedMessage(self.config.server_id, self.term,
                               list(self.votes_for_term.values()))

        # If have >= 2f + 1 votes, we are now elected
        if len(self.votes_for_term) >= self.config.quorum_size:
            print('Received 2f + 1 votes for term %d, becoming leader' % self.term)
            pl_state = PreLeader(self.term, proof, self)
            final_state = pl_state.check_if_catchup_necessary()
            return final_state

        # If this was our (f + 1)th vote, send a vote request
        elif len(self.votes_for_term) == self.config.f + 1:
            print('Received f + 1 votes, sending vote req')
            self.send_vote_request()
        return self

    def start(self):
        '''On startup, a candidate sets an election timeout and waits for
        votes.'''
        pass  # TODO
