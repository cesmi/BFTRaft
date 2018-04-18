

class LogEntry(object):
    def __init__(self, term: int, prev_incremental_hash: bytes,
                 operation: str, client_id: int) -> None:
        self.term = term
        self.prev_incremental_hash = prev_incremental_hash
        self.operation = operation
        self.client_id = client_id

    def incremental_hash(self) -> bytes:
        '''Calculates the hash of the previous incremental hash appended to
        this log entry.'''
        pass  # TODO
