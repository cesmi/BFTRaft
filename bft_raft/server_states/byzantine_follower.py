import time
from ..messages import (ACert, AppendEntriesRequest, AppendEntriesSuccess,
                        SignedMessage)
from .normal_operation_base import NormalOperationBase
from .state import State

from .follower import Follower, FollowerHeartbeatTimeout

class ByzantineFollower0(Follower):
    @staticmethod
    def construct(uncorrupted):
        return ByzantineFollower0(uncorrupted.term, uncorrupted.leader_commit_idx, 
                uncorrupted.leader_a_cert, uncorrupted)

    def __init__(self, term: int, leader_commit_idx: int,
                 leader_a_cert: ACert, copy_from: State) -> None:
        print('ByzantineFollower0')
        super(ByzantineFollower0, self).__init__(term, leader_commit_idx, 
                leader_a_cert, copy_from)
