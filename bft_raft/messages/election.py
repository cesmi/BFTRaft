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
        if not isinstance(self.a_cert, ACert):
            return False
        if not self.a_cert.verify(config):
            return False
        return super(VoteMessage, self).verify(config)

    def update_hash(self, h) -> None:
        if self.a_cert is not None:
            h.update(self.a_cert.hash())
        super(VoteMessage, self).update_hash(h)


class VotesListMessage(ServerMessage):
    '''Base class for a message containing a list of votes.'''

    def __init__(self, sender_id: int, term: int,
                 votes: List[SignedMessage[VoteMessage]]) -> None:
        super(VotesListMessage, self).__init__(sender_id, term)
        self.votes = votes

    def verify(self, config: BaseConfig) -> bool:
        if not super(VotesListMessage, self).verify(config):
            return False
        seen_servers = set()  # type: ignore
        for v in self.votes:
            if not isinstance(v, SignedMessage):
                return False
            if not isinstance(v.message, VoteMessage):
                return False
            if not v.verify(config):
                return False
            if v.sender_id in seen_servers:
                return False  # votes should be from distinct servers
            seen_servers.add(v.sender_id)
        return True

    def update_hash(self, h) -> None:
        for v in self.votes:
            h.update(v.hash())
        super(VotesListMessage, self).update_hash(h)


class VoteRequest(VotesListMessage):
    '''Sent by a candidate to clients after receiving f + 1
    votes (i.e. at least 1 vote from a correct server).'''

    def verify(self, config: BaseConfig) -> bool:
        if not super(VoteRequest, self).verify(config):
            return False
        if not len(self.votes) >= config.f + 1:
            return False
        return True


class ElectedMessage(VotesListMessage):
    '''Sent by a new leader to prove its election. The votes
    list must contain >= 2f + 1 votes.'''

    def verify(self, config: BaseConfig) -> bool:
        if not super(ElectedMessage, self).verify(config):
            return False
        if not len(self.votes) >= config.quorum_size:
            return False
        return True

    def leader_commit_idx(self) -> Tuple[int, ACert]:
        '''Returns the commit index of the new leader based on the
        view numbers/slot numbers of the A-certificates contained in the
        election quorum. Also returns the corresponding A-certificate.'''
        cert = max((m.message.a_cert for m in self.votes
                    if m.message.a_cert is not None),
                   key=lambda cert: (cert.term, cert.slot),
                   default=None)
        if cert is not None:
            return (cert.slot, cert)
        return (None, None)


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

    def update_hash(self, h) -> None:
        h.update(self.int_to_bytes(self.first_slot))
        h.update(self.int_to_bytes(self.last_slot))
        super(CatchupRequest, self).update_hash(h)


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

    def update_hash(self, h) -> None:
        h.update(self.int_to_bytes(self.first_slot))
        for entry in self.entries:
            h.update(entry.hash())
        super(CatchupResponse, self).update_hash(h)
