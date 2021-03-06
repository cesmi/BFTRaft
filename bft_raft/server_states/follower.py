import time
from ..messages import (ACert, AppendEntriesRequest, AppendEntriesSuccess,
                        SignedMessage, ClientViewChangeRequest)
from .normal_operation_base import NormalOperationBase
from .state import State


class Follower(NormalOperationBase):
    def __init__(self, term: int, leader_commit_idx: int,
                 leader_a_cert: ACert, copy_from: State) -> None:
        super(Follower, self).__init__(term, copy_from)
        self.leader_commit_idx = leader_commit_idx
        self.leader_a_cert = leader_a_cert
        self.latest_slot_for_current_term = None  # type: int
        self.last_append_entries_time = time.time()
        self.server.timeout_manager.set_timeout(
            self.config.timeout, FollowerHeartbeatTimeout())

    def on_append_entries_request(self, msg: AppendEntriesRequest,
                                  signed: SignedMessage[AppendEntriesRequest]) -> State:

        # Sender must be the leader of the current term.
        if msg.term != self.term:
            if msg.term > self.term:
                self._request_election_proof(msg.term)
            return self
        if msg.term % self.config.num_servers != msg.sender_id:
            return self

        # If no entries sent, this is a heartbeat
        if not msg.entries:
            self.last_append_entries_time = time.time()
            if len(self.log) < msg.first_slot:
                self._request_log_resend(len(self.log))
            return self

        # Check that message's incremental hash matches ours
        first_entry = msg.entries[0]
        first_slot = msg.first_slot
        last_slot = msg.last_slot
        if len(self.log) < first_slot:
            self._request_log_resend(len(self.log))
            return self
        if first_slot > 0 and first_entry.prev_incremental_hash != \
                self.log[first_slot - 1].incremental_hash():
            return self

        # At least one slot must be greater than leader commit idx
        if self.leader_commit_idx is not None and last_slot <= self.leader_commit_idx:
            return self

        # If leader commit index is in range [first_slot, last_slot], check
        # that entries conform to the leader a cert
        # (by checking incremental hash at leader_commit_idx)
        if self.leader_commit_idx is not None \
                and first_slot <= self.leader_commit_idx \
                and self.leader_commit_idx <= last_slot:
            entry_idx = self.leader_commit_idx - first_slot
            if msg.entries[entry_idx].incremental_hash != \
                    self.leader_a_cert.incremental_hash:
                return self

        # Don't re-append at slots where we already have an entry for the
        # current term
        if self.latest_slot_for_current_term is not None:
            first_to_append = max([self.latest_slot_for_current_term + 1,
                                   first_slot])
        else:
            first_to_append = first_slot
        first_idx = first_to_append - first_slot
        assert first_idx >= 0

        # Append the entries and broadcast response
        self.log = self.log[:first_to_append] + msg.entries[first_idx:]
        self.log = self.log[:first_slot] + msg.entries
        resp = AppendEntriesSuccess(
            self.config.server_id, self.term,
            last_slot, self.log[-1].incremental_hash())
        self.server.messenger.broadcast_server_message(resp)
        self._add_append_entries_success(
            resp, SignedMessage(resp, self.config.private_key))
        self._add_append_entries_success(
            msg.leader_success.message, msg.leader_success)

        self.last_append_entries_time = time.time()

        if self.log:
            self.latest_slot_for_current_term = len(self.log) - 1
        return self

    def on_client_view_change_request(self, msg: ClientViewChangeRequest,
                                      signed: SignedMessage[ClientViewChangeRequest]) -> 'State':
        return self.increment_term()

    def on_timeout(self, context: object) -> State:
        if isinstance(context, FollowerHeartbeatTimeout):
            return self.on_heartbeat_timeout()
        else:
            return super(Follower, self).on_timeout(context)

    def on_heartbeat_timeout(self) -> State:
        if time.time() - self.last_append_entries_time > self.config.timeout:
            return self.increment_term()
        else:
            self.server.timeout_manager.set_timeout(
                self.config.timeout, FollowerHeartbeatTimeout())
            return self


class FollowerHeartbeatTimeout(object):
    pass
