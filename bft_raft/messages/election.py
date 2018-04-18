from typing import List, Tuple
from .base import ServerMessage, SignedMessage
from .commit import ACert
from ..config import ServerConfig


class VoteMessage(ServerMessage):
    def __init__(self, sender_id: int, term: int,
                 a_cert: ACert) -> None:
        super(VoteMessage, self).__init__(sender_id, term)
        self.a_cert = a_cert


class VoteRequest(ServerMessage):
    '''Sent by a candidate to clients after receiving f + 1
    votes (i.e. at least 1 vote from a correct server).'''

    def __init__(self, sender_id: int, term: int,
                 votes: List[SignedMessage[VoteMessage]]) -> None:
        super(VoteRequest, self).__init__(sender_id, term)
        self.votes = votes

    def verify(self, config: ServerConfig) -> bool:
        return True  # TODO


class ElectedMessage(ServerMessage):
    '''Sent by a new leader to prove its election. The votes
    list must contain >= 2f + 1 votes.'''

    def __init__(self, sender_id: int, term: int,
                 votes: List[SignedMessage[VoteMessage]]) -> None:
        super(ElectedMessage, self).__init__(sender_id, term)
        self.votes = votes

    def verify(self, config: ServerConfig) -> bool:
        return True  # TODO

    def leader_commit_idx(self) -> Tuple[int, ACert]:
        return (0, None)  # TODO
