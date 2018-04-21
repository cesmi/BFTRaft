from typing import List

from .log_entry import LogEntry
from .base import ServerMessage


class AppendEntriesRequest(ServerMessage):
    def __init__(self, sender_id: int, term: int,
                 prev_log_index: int, prev_log_term: int,
                 entries: List[LogEntry],
                 leader_commit: int) -> None:
        super(AppendEntriesRequest, self).__init__(sender_id, term)
        self.prev_log_index = prev_log_index
        self.prev_log_term = prev_log_term
        self.entries = entries
        self.leader_commit = leader_commit


class AppendEntriesResponse(ServerMessage):
    def __init__(self, sender_id: int, term: int,
                 slot: int, success: bool) -> None:
        super(AppendEntriesResponse, self).__init__(sender_id, term)
        self.slot = slot
        self.success = success
