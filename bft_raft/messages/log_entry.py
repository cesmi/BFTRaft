from typing import List

from ..config import BaseConfig
from .base import SignedMessage
from .client_request import ClientRequest
from .hashable import Hashable


class LogEntry(Hashable):
    def __init__(self, term: int, prev_incremental_hash: bytes,
                 client_request: SignedMessage[ClientRequest]) -> None:
        self.term = term
        self.prev_incremental_hash = prev_incremental_hash
        self.request = client_request

    def incremental_hash(self) -> bytes:
        return self.hash()

    @property
    def client_id(self):
        return self.request.sender_id

    @property
    def seqno(self):
        return self.request.message.seqno

    @property
    def operation(self):
        return self.request.message.operation

    def update_hash(self, h) -> None:
        h.update(self.int_to_bytes(self.term))
        h.update(self.prev_incremental_hash)
        h.update(self.request.hash())

    def verify(self, config: BaseConfig) -> bool:
        return True  # TODO


def verify_entries(entries: List[LogEntry], config: BaseConfig) -> bool:
    '''Verifies that a list of log entries have matching incremental hashes
    and contain requests signed by clients.'''
    for entry in entries:
        if not isinstance(entry, LogEntry):
            return False
        if not entry.verify(config):
            return False
        for i in range(1, len(entries)):
            a = entries[i - 1]
            b = entries[i]
            if a.incremental_hash() != b.prev_incremental_hash:
                return False
    return True
