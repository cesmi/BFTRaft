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
    @staticmethod
    def construct(uncorrupted):
        return ByzantineCandidate0(uncorrupted.term, uncorrupted.votes_for_term, 
                uncorrupted.server, uncorrupted)

    def __init__(self, term: int, votes_for_term: Dict[int, SignedMessage[VoteMessage]],
                 server: BaseServer, copy_from: State) -> None:
        print('ByzantineCandidate0')
        super(ByzantineCandidate0, self).__init__(term, votes_for_term, server, copy_from)

