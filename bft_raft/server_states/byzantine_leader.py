from ..messages import (ClientRequest, ClientViewChangeRequest, ElectedMessage,
                        SignedMessage)
from .leader import Leader
from .state import State


class ByzantineLeader0(Leader):
    @staticmethod
    def construct(uncorrupted):
        return ByzantineLeader0(uncorrupted.term, uncorrupted.election_proof,
                                uncorrupted)

    def __init__(self, term: int,
                 election_proof: ElectedMessage,
                 copy_from: State) -> None:
        self.config.log('ByzantineLeader0 ctor')
        super(ByzantineLeader0, self).__init__(term, election_proof, copy_from)

    # Ignore client requests
    def on_client_request(self, msg: ClientRequest,
                          signed: SignedMessage[ClientRequest]):
        # ignore the message
        return self

    def on_client_view_change_request(self, msg: ClientViewChangeRequest,
                                      signed: SignedMessage[ClientViewChangeRequest]):
        return self  # ignore


class LeaderHeartbeatTimeout(object):
    pass
