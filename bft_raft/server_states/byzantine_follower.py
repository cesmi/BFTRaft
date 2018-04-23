from ..messages import ACert
from .follower import Follower
from .state import State


class ByzantineFollower0(Follower):
    @staticmethod
    def construct(uncorrupted: Follower):
        return ByzantineFollower0(uncorrupted.term, uncorrupted.leader_commit_idx,
                                  uncorrupted.leader_a_cert, uncorrupted)

    def __init__(self, term: int, leader_commit_idx: int,
                 leader_a_cert: ACert, copy_from: State) -> None:
        self.config.log('ByzantineFollower0 ctor')
        super(ByzantineFollower0, self).__init__(term, leader_commit_idx,
                                                 leader_a_cert, copy_from)
