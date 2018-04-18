from ..log_entry import LogEntry
from ..messages import (ACert, AppendEntriesRequest, AppendEntriesSuccess,
                        ClientRequest, SignedMessage)
from .normal_operation_base import NormalOperationBase
from .state import State


class Leader(NormalOperationBase):
    def __init__(self, term: int, commit_idx: int,
                 commit_idx_a_cert: ACert, copy_from: State) -> None:
        super(Leader, self).__init__(term, commit_idx,
                                     commit_idx_a_cert, copy_from)
        if commit_idx is not None and self.applied_c_cert is not None:
            self.log = self.log[0:commit_idx]
            assert self.applied_c_cert.slot < commit_idx
        else:
            self.log = []
            assert self.applied_c_cert is None

    def on_client_request(self, msg: ClientRequest,
                          signed: SignedMessage[ClientRequest]):

        # Build an AppendEntriesRequest to send to other servers
        prev_ihash = b'0'
        if self.log:  # log not empty
            prev_ihash = self.log[-1].incremental_hash()
        entry = LogEntry(self.term, prev_ihash, msg.operation,
                         msg.sender_id)
        slot = len(self.log)
        request = AppendEntriesRequest(self.config.server_id, self.term,
                                       entry, slot, signed)
        self.server.messenger.broadcast_server_message(request)

        # Add the entry to our own log
        self.log.append(entry)
        success = AppendEntriesSuccess(self.config.server_id, self.term, slot,
                                       entry.incremental_hash())
        self._add_append_entries_success(
            SignedMessage(success, self.config.private_key))
        return self

    def start(self):
        assert False  # A server is never in this state initially
