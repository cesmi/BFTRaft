from typing import List, Tuple
from .base import ServerMessage, SignedMessage
from .commit import ACert
from ..config import BaseConfig
from .log_entry import LogEntry, verify_entries


class VoteMessage(ServerMessage):
    def __init__(self, sender_id: int, term: int,
                 a_cert: ACert) -> None:
        super(VoteMessage, self).__init__(sender_id, term)
        self.a_cert = a_cert

    def verify(self, config: BaseConfig) -> bool:
        return True  # TODO


class VoteRequest(ServerMessage):
    '''Sent by a candidate to clients after receiving f + 1
    votes (i.e. at least 1 vote from a correct server).'''

    def __init__(self, sender_id: int, term: int,
                 votes: List[SignedMessage[VoteMessage]]) -> None:
        super(VoteRequest, self).__init__(sender_id, term)
        self.votes = votes

    def verify(self, config: BaseConfig) -> bool:
        return True  # TODO


class ElectedMessage(ServerMessage):
    '''Sent by a new leader to prove its election. The votes
    list must contain >= 2f + 1 votes.'''

    def __init__(self, sender_id: int, term: int,
                 votes: List[SignedMessage[VoteMessage]]) -> None:
        super(ElectedMessage, self).__init__(sender_id, term)
        self.votes = votes

    def verify(self, config: BaseConfig) -> bool:
        return True  # TODO

    def leader_commit_idx(self) -> Tuple[int, ACert]:
        '''Returns the commit index of the new leader based on the
        view numbers/slot numbers of the A-certificates contained in the
        election quorum. Also returns the corresponding A-certificate.'''
        return (None, None)  # TODO


class ElectionProofRequest(ServerMessage):
    '''Sent by a server to the primary to request proof of its election.'''
    pass  # (nothing needs to be added here)


class CatchupRequest(ServerMessage):
    '''Sent by a new leader to a servers to request log entries at slots
    <= the commit index that it does not have.'''

    def __init__(self, sender_id: int, term: int,
                 first_slot: int, last_slot: int) -> None:
        super(CatchupRequest, self).__init__(sender_id, term)
        self.first_slot = first_slot
        self.last_slot = last_slot

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.first_slot, int) or self.first_slot < 0:
            return False
        if not isinstance(self.last_slot, int) or self.last_slot < self.first_slot:
            return False
        return super(CatchupRequest, self).verify(config)


class CatchupResponse(ServerMessage):
    def __init__(self, sender_id: int, term: int,
                 first_slot: int, entries: List[LogEntry]) -> None:
        super(CatchupResponse, self).__init__(sender_id, term)
        self.first_slot = first_slot
        self.entries = entries

    @property
    def last_slot(self):
        return self.first_slot + len(self.entries) - 1

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.first_slot, int) or self.first_slot < 0:
            return False
        if not verify_entries(self.entries, config):
            return False
        return super(CatchupResponse, self).verify(config)
