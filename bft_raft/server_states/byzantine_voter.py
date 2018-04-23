from ..servers.base import BaseServer
from .state import State
from .voter import Voter
from .byzantine_candidate import ByzantineCandidate0


class ByzantineVoter0(Voter):
    @staticmethod
    def construct(uncorrupted: Voter):
        return ByzantineCandidate0(uncorrupted.term, {}, uncorrupted.server, uncorrupted)

    def __init__(self, term: int,
                 server: BaseServer,
                 copy_from: State) -> None:
        self.config.log('ByzantineVoter0 ctor')
        super(ByzantineVoter0, self).__init__(term, server, copy_from)
