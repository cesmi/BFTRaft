import time
from ..messages import (ACert, AppendEntriesRequest, AppendEntriesSuccess,
                        SignedMessage)
from .normal_operation_base import NormalOperationBase
from .state import State

from .follower import Follower, FollowerHeartbeatTimeout

class ByzantineFollower0(Follower):
    def __init__(self, term: int, leader_commit_idx: int,
                 leader_a_cert: ACert, copy_from: State) -> None:
        print('ByzantineFollower0')
        super(ByzantineFollower0, self).__init__(term, leader_commit_idx, 
                leader_a_cert, copy_from)

    def on_append_entries_request(self, msg: AppendEntriesRequest,
                                  signed: SignedMessage[AppendEntriesRequest]) -> State:
        super(ByzantineFollower0, self).on_append_entries_request(msg, signed)
        return self

    def on_timeout(self, context: object) -> State:
        super(ByzantineFollower0, self).on_timeout(context)
        return self

    def on_heartbeat_timeout(self) -> State:
        super(ByzantineFollower0, self).on_heartbeat_timeout()
        return self

    def start(self) -> None:
        super(ByzantineFollower0, self).start()
