from typing import List
from ..config import BaseConfig
from ..log_entry import LogEntry


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
