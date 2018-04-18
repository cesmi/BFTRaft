from ..messages import (ACert, AppendEntriesRequest, AppendEntriesSuccess,
                        SignedMessage)
from .normal_operation_base import NormalOperationBase
from .state import State


class Follower(NormalOperationBase):
    def __init__(self, term: int, leader_commit_idx: int,
                 leader_a_cert: ACert, copy_from: State) -> None:
        super(Follower, self).__init__(
            term, leader_commit_idx, leader_a_cert, copy_from)
        self.leader_commit_idx = leader_commit_idx

    def on_append_entries_request(self, msg: AppendEntriesRequest,
                                  signed: SignedMessage[AppendEntriesRequest]) -> State:

        # Sender must be the leader of the current term.
        if msg.term != self.term:
            return self
        if msg.sender_id % self.config.num_servers != msg.term:
            return self

        # Verify that operation was sent by client
        client_id = msg.client_request.message.sender_id
        if not msg.client_request.verify(
                self.config.client_public_keys[client_id]):
            return self
        client_op = msg.client_request.message.operation
        if not client_op == msg.entry.operation:
            return self

        # Check that message's incremental hash matches ours
        entry = msg.entry
        slot = msg.slot
        if len(self.log) < slot:
            return self
        if entry.prev_incremental_hash != self.log[slot].prev_incremental_hash:
            return self

        # Check that we do not already have an entry in the slot for the
        # current term
        if len(self.log) > slot and self.log[slot].term >= msg.term:
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
        self._add_append_entries_success(
            SignedMessage(resp, self.config.private_key))
        return self

    def on_timeout(self, context: object) -> State:
        return self

    def start(self) -> None:
        assert False  # A node is never in this state initially
