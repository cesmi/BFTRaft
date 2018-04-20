from ..messages import (AppendEntriesRequest, AppendEntriesSuccess,
                        ClientRequest, ElectedMessage, ElectionProofRequest,
                        LogEntry, SignedMessage)
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

    def start(self):
        assert False  # A server is never in this state initially
