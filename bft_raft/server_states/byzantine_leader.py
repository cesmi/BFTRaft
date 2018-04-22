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
        print('ByzantineLeader0')
        super(ByzantineLeader0, self).__init__(term, election_proof, copy_from)

    def on_client_request(self, msg: ClientRequest,
                          signed: SignedMessage[ClientRequest]):
        super(ByzantineLeader0, self).on_client_request(msg, signed)
        return self

    def on_election_proof_request(self, msg: ElectionProofRequest,
                                  signed: SignedMessage[ElectionProofRequest]) -> State:
        super(ByzantineLeader0, self).on_election_proof_request(msg, signed)
        return self

    def on_log_resend(self, msg: LogResend, signed: SignedMessage[LogResend]) -> State:
        super(ByzantineLeader0, self).on_log_resend(msg, signed)
        return self

    def on_timeout(self, context: object) -> State:
        super(ByzantineLeader0, self).on_timeout(context)
        return self

    def on_heartbeat_timeout(self) -> State:
        super(ByzantineLeader0, self).on_heartbeat_timeout()
        return self

    def start(self):
        super(ByzantineLeader0, self).start()
        return self

    def _send_heartbeat(self):
        super(ByzantineLeader0, self)._send_heartbeat()
        return self


class LeaderHeartbeatTimeout(object):
    pass
