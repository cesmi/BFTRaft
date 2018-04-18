import pickle
from Crypto.Hash import SHA256


class LogEntry(object):
    def __init__(self, term: int, prev_incremental_hash: bytes,
                 operation: str, client_id: int) -> None:
        self.term = term
        self.prev_incremental_hash = prev_incremental_hash
        self.operation = operation
        self.client_id = client_id

    def incremental_hash(self) -> bytes:
        return SHA256.new(pickle.dumps(self)).digest()
