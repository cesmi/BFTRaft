from ..messages import (CatchupRequest, CatchupResponse, ElectedMessage,
                        SignedMessage)
from .state import State


class PreLeader(State):
    def __init__(self, term: int,
                 election_proof: ElectedMessage,
                 copy_from: State) -> None:
        super(PreLeader, self).__init__(copy_from.server, copy_from, term)
        self.election_proof = election_proof
        self.commit_idx, self.commit_idx_a_cert = election_proof.leader_commit_idx()
        if self.applied_c_cert is not None:
            self.log = self.log[:self.applied_c_cert.slot + 1]
            assert self.applied_c_cert.slot <= self.commit_idx
        else:
            self.log = []

    def check_if_catchup_necessary(self) -> State:
        '''If sending a catchup request to followers and waiting for replies is
        necessary, sends the message. Otherwise, transitions immediately to leader state.'''
        from .leader import Leader
        if self.commit_idx is not None and len(self.log) <= self.commit_idx:
            self.send_catchup_request()
            return self
        else:
            return Leader(self.term, self.election_proof, self)

    def send_catchup_request(self):
        '''Sends a request for log entries at slots <= commit index that the
        newly elected leader doesn't have yet.'''
        req = CatchupRequest(self.config.server_id, self.term,
                             len(self.log), self.commit_idx)
        self.server.messenger.broadcast_server_message(req)

    def on_catchup_response(self, msg: CatchupResponse,
                            signed: SignedMessage[CatchupResponse]) -> State:
        from .leader import Leader
        assert len(self.log) <= self.commit_idx
        if not msg.entries:  # (no entries sent)
            return self
        if msg.first_slot != len(self.log):
            return self
        if msg.last_slot != self.commit_idx:
            return self
        if msg.entries[-1].incremental_hash() != self.commit_idx_a_cert.incremental_hash:
            return self
        assert msg.entries[-1].term == self.commit_idx_a_cert.term

        # Append entries to log and transition to leader state
        self.log += msg.entries
        assert len(self.log) == self.commit_idx + 1
        return Leader(self.term, self.election_proof, self)

    def start(self):
        assert False  # A server is never in this state initially
