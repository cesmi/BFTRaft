from typing import Dict

from ..messages import SignedMessage, VoteMessage
from ..servers.base import BaseServer
from .candidate import Candidate
from .state import State


class ByzantineCandidate0(Candidate):
    @staticmethod
    def construct(uncorrupted: Candidate):
        return ByzantineCandidate0(uncorrupted.term, uncorrupted.votes_for_term,
                                   uncorrupted.server, uncorrupted)

    def __init__(self, term: int, votes_for_term: Dict[int, SignedMessage[VoteMessage]],
                 server: BaseServer, copy_from: State) -> None:
        self.config.log('ByzantineCandidate0 ctor')
        super(ByzantineCandidate0, self).__init__(term, votes_for_term, server, copy_from)
