import pickle
from typing import List

from Crypto.Hash import SHA256

from ..config import BaseConfig
from .base import SignedMessage
from .client_request import ClientRequest


class LogEntry(object):
    def __init__(self, term: int, prev_incremental_hash: bytes,
                 client_request: SignedMessage[ClientRequest],
                 client_id: int, seqno: int,
                 operation: bytes) -> None:
        self.term = term
        self.prev_incremental_hash = prev_incremental_hash
        self.signed = client_request

        self.client_id = client_id
        self.seqno = seqno
        self.operation = operation

    def incremental_hash(self) -> bytes:
        return SHA256.new(pickle.dumps(self)).digest()

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
