from typing import Dict

from ..messages import ElectedMessage, SignedMessage, VoteMessage, VoteRequest
from ..servers.base import BaseServer
from .state import State

from .candidate import Candidate

class ByzantineCandidate0(Candidate):
    def __init__(self, term: int, votes_for_term: Dict[int, SignedMessage[VoteMessage]],
                 server: BaseServer, copy_from: State) -> None:
        super(ByzantineCandidate0, self).__init__(term, votes_for_term, server, copy_from)

    def send_vote_request(self):
        super(ByzantineCandidate0, self).send_vote_request()

    def on_vote(self, msg: VoteMessage,
                signed: SignedMessage[VoteMessage]) -> State:
        print('Byzantine Candidate got vote!')
        return super(ByzantineCandidate0, self).on_vote(msg, signed)
