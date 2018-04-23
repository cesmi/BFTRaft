from ..messages import (AppendEntriesRequest, AppendEntriesSuccess,
                        ClientRequest, ElectedMessage,
                        ElectionProofRequest, LogEntry, LogResend,
                        SignedMessage)
from .normal_operation_base import NormalOperationBase
from .state import State


class Leader(NormalOperationBase):
    def __init__(self, term: int,
                 election_proof: ElectedMessage,
                 copy_from: State) -> None:
        super(Leader, self).__init__(term, copy_from)
        self.election_proof = election_proof
        commit_idx, _ = election_proof.leader_commit_idx()
        if commit_idx is not None:
            assert commit_idx == len(self.log) - 1
        else:
            assert not self.log  # empty log
        self._send_heartbeat()

    def on_client_request(self, msg: ClientRequest,
                          signed: SignedMessage[ClientRequest]):

        # Add the entry to our own log
        prev_ihash = b'0'
        if self.log:  # log not empty
            prev_ihash = self.log[-1].incremental_hash()
        entry = LogEntry(self.term, prev_ihash, signed)
        slot = len(self.log)
        self.log.append(entry)
        success = AppendEntriesSuccess(self.config.server_id, self.term, slot,
                                       entry.incremental_hash())
        signed_success = SignedMessage(success, self.config.private_key)
        self._add_append_entries_success(success, signed_success)

        # Build an AppendEntriesRequest to send to other servers
        request = AppendEntriesRequest(self.config.server_id, self.term,
                                       [entry], slot, signed_success)
        self.server.messenger.broadcast_server_message(request)
        return self

    def on_election_proof_request(self, msg: ElectionProofRequest,
                                  signed: SignedMessage[ElectionProofRequest]) -> State:
        self.server.messenger.send_server_message(
            msg.sender_id, self.election_proof)
        return self

    def on_log_resend(self, msg: LogResend, signed: SignedMessage[LogResend]) -> State:
        if msg.log_len < 0 or msg.log_len >= len(self.log):
            return self

        # Build the most recent AppendEntriesRequest and send
        success = AppendEntriesSuccess(
            self.config.server_id, self.term,
            len(self.log) - 1, self.log[-1].incremental_hash())
        signed_success = SignedMessage(success, self.config.private_key)
        old_request = AppendEntriesRequest(
            self.config.server_id, self.term,
            self.log[msg.log_len:], msg.log_len, signed_success)
        self.server.messenger.send_server_message(msg.sender_id, old_request)
        return self

    def on_timeout(self, context: object) -> State:
        if isinstance(context, LeaderHeartbeatTimeout):
            return self.on_heartbeat_timeout()
        else:
            return super(Leader, self).on_timeout(context)

    def on_heartbeat_timeout(self) -> State:
        self._send_heartbeat()
        return self

    def _send_heartbeat(self):
        self.server.timeout_manager.set_timeout(
            self.config.timeout / 2, LeaderHeartbeatTimeout())
        msg = AppendEntriesRequest(self.config.server_id, self.term,
                                   [], len(self.log), None)
        self.server.messenger.broadcast_server_message(msg)


class LeaderHeartbeatTimeout(object):
    pass
