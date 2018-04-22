from ..messages import (AppendEntriesRequest, AppendEntriesSuccess,
                        CommitMessage, ElectedMessage, SignedMessage,
                        VoteMessage)
from ..servers.base import BaseServer
from .state import State

from .voter import Voter

class ByzantineVoter0(Voter):
    @staticmethod
    def construct(uncorrupted):
        return ByzantineVoter0(uncorrupted.term, uncorrupted.server, uncorrupted)

    def __init__(self, term: int,
                 server: BaseServer,
                 copy_from: State) -> None:
        print('ByzantineVoter0')
        super(ByzantineVoter0, self).__init__(term, server, copy_from)
