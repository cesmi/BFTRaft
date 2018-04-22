from ..messages import (AppendEntriesRequest, AppendEntriesSuccess, LogResend,
                        ClientRequest, ElectedMessage, ElectionProofRequest,
                        LogEntry, SignedMessage)
from .normal_operation_base import NormalOperationBase
from .state import State

from .leader import Leader

class ByzantineLeader0(Leader):
    @staticmethod
    def construct(uncorrupted):
        return ByzantineLeader0(uncorrupted.term, uncorrupted.election_proof, 
                uncorrupted)

    def __init__(self, term: int,
                 election_proof: ElectedMessage,
                 copy_from: State) -> None:
        print('ByzantineLeader0')
        super(ByzantineLeader0, self).__init__(term, election_proof, copy_from)


class LeaderHeartbeatTimeout(object):
    pass
