from typing import List

from ..config import BaseConfig
from .log_entry import LogEntry, verify_entries
from .base import ServerMessage, SignedMessage


class AppendEntriesSuccess(ServerMessage):
    def __init__(self, sender_id: int, term: int,
                 slot: int, incremental_hash: bytes) -> None:
        super(AppendEntriesSuccess, self).__init__(sender_id, term)
        self.incremental_hash = incremental_hash
        self.slot = slot

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.incremental_hash, bytes):
            return False
        if not isinstance(self.slot, int) or self.slot < 0:
            return False
        return super(AppendEntriesSuccess, self).verify(config)

    def update_hash(self, h) -> None:
        h.update(self.incremental_hash)
        h.update(self.int_to_bytes(self.slot))
        super(AppendEntriesSuccess, self).update_hash(h)


class AppendEntriesRequest(ServerMessage):
    def __init__(self, sender_id: int, term: int,
                 entries: List[LogEntry], first_slot: int,
                 leader_success: SignedMessage[AppendEntriesSuccess]) -> None:
        super(AppendEntriesRequest, self).__init__(sender_id, term)
        self.entries = entries
        self.first_slot = first_slot
        self.leader_success = leader_success

    @property
    def last_slot(self):
        return self.first_slot + len(self.entries) - 1

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.first_slot, int) or not isinstance(self.entries, list):
            return False
        if self.first_slot < 0:
            return False
        if not verify_entries(self.entries, config):
            return False
        # if there is no success message enclosed (i.e. this message is a heartbeat)
        # the entries list should be empty
        if self.leader_success is None and self.entries:
            return False
        # if there is a success message encloesd, verify it
        elif self.leader_success is not None:
            if not isinstance(self.leader_success, AppendEntriesSuccess):
                return False
            if not self.leader_success.verify(config):
                return False
        return super(AppendEntriesRequest, self).verify(config)

    def update_hash(self, h) -> None:
        for entry in self.entries:
            h.update(entry.incremental_hash())
        h.update(self.int_to_bytes(self.first_slot))
        if self.leader_success is not None:
            h.update(self.leader_success.hash())
        super(AppendEntriesRequest, self).update_hash(h)


class LogResend(ServerMessage):
    def __init__(self, sender_id: int, term: int, log_len: int) -> None:
        super(LogResend, self).__init__(sender_id, term)
        self.log_len = log_len

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.log_len, int) or self.log_len < 0:
            return False
        return super(LogResend, self).verify(config)

    def update_hash(self, h) -> None:
        h.update(self.int_to_bytes(self.log_len))
        super(LogResend, self).update_hash(h)
