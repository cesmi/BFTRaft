from ..log_entry import LogEntry
from ..messages import (AppendEntriesRequest, AppendEntriesSuccess,
                        ClientRequest, ElectedMessage, ElectionProofRequest,
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
        assert commit_idx == len(self.log) - 1

    def on_client_request(self, msg: ClientRequest,
                          signed: SignedMessage[ClientRequest]):

        # Build an AppendEntriesRequest to send to other servers
        prev_ihash = b'0'
        if self.log:  # log not empty
            prev_ihash = self.log[-1].incremental_hash()
        entry = LogEntry(self.term, prev_ihash, signed)
        slot = len(self.log)
        request = AppendEntriesRequest(self.config.server_id, self.term,
                                       [entry], slot)
        self.server.messenger.broadcast_server_message(request)

        # Add the entry to our own log
        self.log.append(entry)
        success = AppendEntriesSuccess(self.config.server_id, self.term, slot,
                                       entry.incremental_hash())
        self._add_append_entries_success(
            SignedMessage(success, self.config.private_key))
        return self

    def on_election_proof_request(self, msg: ElectionProofRequest,
                                  signed: SignedMessage[ElectionProofRequest]) -> State:
        self.server.messenger.send_server_message(
            msg.sender_id, self.election_proof)
        return self

    def start(self):
        assert False  # A server is never in this state initially
