from ..messages import (CatchupRequest, CatchupResponse, ElectedMessage,
                        SignedMessage, ElectionProofRequest)
from .state import State


class ByzantinePreLeader0(State):
    def __init__(self, term: int,
                 election_proof: ElectedMessage,
                 copy_from: State) -> None:
        print('PreLeader0')
        super(ByzantinePreLeader0, self).__init__(term, election_proof, copy_from)

    def check_if_catchup_necessary(self) -> State:
        from .byzantine_leader import ByzantinePreLeader0
        next_state = super(ByzantinePreLeader0, self).check_if_catchup_necessary()
        if isinstance(next_state, Leader):
            return ByzantineLeader0(self.term, self.election_proof, self)
        else:
            return self

    def on_catchup_response(self, msg: CatchupResponse,
                            signed: SignedMessage[CatchupResponse]) -> State:
        from .byzantine_leader import ByzantineLeader0
        super(ByzantinePreLeader0, self).on_catchup_response(msg, signed)
        return ByzantineLeader0(self.term, self.election_proof, self)
