from typing import Dict

from ..messages import ElectedMessage, SignedMessage, VoteMessage, VoteRequest
from ..servers.base import BaseServer
from .state import State

from .candidate import Candidate

from .pre_leader import PreLeader
from .leader import Leader
from .byzantine_preleader import ByzantinePreLeader0
from .byzantine_leader import ByzantineLeader0

class ByzantineCandidate0(Candidate):
    def __init__(self, term: int, votes_for_term: Dict[int, SignedMessage[VoteMessage]],
                 server: BaseServer, copy_from: State) -> None:
        print('ByzantineCandidate0')
        super(ByzantineCandidate0, self).__init__(term, votes_for_term, server, copy_from)

    def send_vote_request(self):
        super(ByzantineCandidate0, self).send_vote_request()

    def on_vote(self, msg: VoteMessage,
                signed: SignedMessage[VoteMessage]) -> State:
        print('On Vote!!!!!!!!!!!!!!!')
        next_state = super(ByzantineCandidate0, self).on_vote(msg, signed)
        proof = ElectedMessage(self.config.server_id, self.term,
                               list(self.votes_for_term.values()))
        if isinstance(next_state, PreLeader):
            return ByzantinePreLeader0(self.term, proof, self)
        elif isinstance(next_state, Leader):
            return ByzantineLeader0(self.term, proof, self)
        return self
