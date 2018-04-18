from ..messages.append_entries import (AppendEntriesRequest,
                                       AppendEntriesSuccess)
from ..messages.base import SignedMessage
from ..messages.commit import ACert
from .normal_operation_base import NormalOperationBase
from .state import State


class Follower(NormalOperationBase):
    def __init__(self, term: int, leader_commit_idx: int,
                 leader_a_cert: ACert, copy_from: State) -> None:
        super(Follower, self).__init__(term, leader_commit_idx, leader_a_cert, copy_from)
        self.leader_commit_idx = leader_commit_idx

    def on_append_entries(self, message: AppendEntriesRequest) -> State:
        '''Called when the server receives an AppendEntriesRequest message.'''

        # Sender must be the leader of the current term.
        if message.term != self.term:
            return self
        if message.sender_id % self.config.num_servers != message.term:
            return self

        # Verify that operation was sent by client
        client_id = message.client_request.message.sender_id
        if not message.client_request.verify(
                self.config.client_public_keys[client_id]):
            return self
        client_op = message.client_request.message.operation
        if not client_op == message.entry.operation:
            return self

        # Check that message's incremental hash matches ours
        entry = message.entry
        slot = message.slot
        if len(self.log) < slot:
            return self
        if entry.prev_incremental_hash != self.log[slot].prev_incremental_hash:
            return self

        # Check that we do not already have an entry in the slot for the
        # current term
        if len(self.log) > slot and self.log[slot].term >= message.term:
            return self

        # Verify that slot number is greater than leader commit index
        if slot <= self.leader_commit_idx:
            return self

        # Append entry to log and broadcast success message
        self.log = self.log[:slot] + [entry]
        resp = AppendEntriesSuccess(
            self.config.server_id, self.term,
            slot, self.log[-1].incremental_hash())
        self.server.messenger.broadcast_server_message(resp)
        self._add_append_entries_success(SignedMessage(resp, self.config.private_key))
        return self

    def on_message(self, msg: SignedMessage) -> State:
        if isinstance(msg.message, AppendEntriesRequest):
            return self.on_append_entries(msg.message)
        return super(Follower, self).on_message(msg)

    def on_timeout(self, context: object) -> State:
        return self

    def start(self) -> None:
        assert False  # A node is never in this state initially
