from ..messages import (AppendEntriesRequest, AppendEntriesSuccess, LogResend,
                        ClientRequest, ElectedMessage, ElectionProofRequest,
                        LogEntry, SignedMessage)
from .normal_operation_base import NormalOperationBase
from .state import State

from .leader import Leader

class ByzantineLeader0(Leader):
    def __init__(self, term: int,
                 election_proof: ElectedMessage,
                 copy_from: State) -> None:
        super(ByzantineLeader0, self).__init__(term, election_proof, copy_from)

    def on_client_request(self, msg: ClientRequest,
                          signed: SignedMessage[ClientRequest]):
        return super(ByzantineLeader0, self).on_client_request(msg, signed)

    def on_election_proof_request(self, msg: ElectionProofRequest,
                                  signed: SignedMessage[ElectionProofRequest]) -> State:
        return super(ByzantineLeader0, self).on_election_proof_request(msg, signed)

    def on_log_resend(self, msg: LogResend, signed: SignedMessage[LogResend]) -> State:
        return super(ByzantineLeader0, self).on_log_resend(msg, signed)

    def on_timeout(self, context: object) -> State:
        return super(ByzantineLeader0, self).on_timeout(context)

    def on_heartbeat_timeout(self) -> State:
        return super(ByzantineLeader0, self).on_heartbeat_timeout()

    def start(self):
        return super(ByzantineLeader0, self).start()

    def _send_heartbeat(self):
        return super(ByzantineLeader0, self)._send_heartbeat()


class LeaderHeartbeatTimeout(object):
    pass
