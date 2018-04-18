from .base import ServerMessage, SignedMessage
from .client_request import ClientRequest
from ..log_entry import LogEntry


class AppendEntriesRequest(ServerMessage):
    def __init__(self, sender_id: int, term: int,
                 entry: LogEntry, slot: int,
                 client_request: SignedMessage[ClientRequest]) -> None:
        super(AppendEntriesRequest, self).__init__(sender_id, term)
        self.entry = entry
        self.slot = slot
        self.client_request = client_request


class AppendEntriesSuccess(ServerMessage):
    def __init__(self, sender_id: int, term: int,
                 slot: int, incremental_hash: bytes) -> None:
        super(AppendEntriesSuccess, self).__init__(sender_id, term)
        self.incremental_hash = incremental_hash
        self.slot = slot
