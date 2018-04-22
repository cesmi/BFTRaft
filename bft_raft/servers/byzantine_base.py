from ..application import Application
from ..config import ServerConfig
from ..messages import Message, SignedMessage
from ..messengers.listener import MessengerListener
from ..messengers.messenger import Messenger
from ..server_states.state import State
from ..timeout_managers.listener import TimeoutListener
from ..timeout_managers.timeout_manager import TimeoutManager

from .base import BaseServer

from ..server_states.candidate import Candidate
from ..server_states.voter import Voter
from ..server_states.follower import Follower
from ..server_states.leader import Leader
from ..server_states.pre_leader import PreLeader

from ..server_states.byzantine_candidate import ByzantineCandidate0
from ..server_states.byzantine_voter import ByzantineVoter0
from ..server_states.byzantine_follower import ByzantineFollower0
from ..server_states.byzantine_leader import ByzantineLeader0
from ..server_states.byzantine_preleader import ByzantinePreLeader0

class ByzantineBaseServer(BaseServer):
    def __init__(self, config: ServerConfig, application: Application,
                 messenger: Messenger, timeout_manager: TimeoutManager,
                 byzantine_type: int) -> None:
        self.byzantine_type = byzantine_type
        super(ByzantineBaseServer, self).__init__(config, application, 
                messenger, timeout_manager)

    def on_message(self, msg: Message, signed: SignedMessage) -> None:
        next_state = super(ByzantineBaseServer, self).on_message(msg, signed)
        assert(next_state != None)
        if isinstance(next_state, Follower):
            return ByzantineFollower0(msg.term, self.votes[msg.term], self.server, self)
        elif isinstance(next_state, Voter):
            return ByzantineVoter0(msg.term, self.server, self)
        elif isinstance(next_state, Candidate):
            return ByzantineCandidate0(next_term, {}, self.server, self)
        elif isinstance(next_state, PreLeader):
            return ByzantinePreLeader0(next_state.term, next_term.election_proof, self)
        elif isinstance(next_state, Leader):
            return ByzantineLeader0(next_state.term, next_term.election_proof, self)
        else:
            print(next_state)
            assert(False)

    def on_timeout(self, context: object) -> None:
        next_state = super(ByzantineBaseServer, self).on_timeout(context)
        if isinstance(next_state, Voter):
            return ByzantineVoter0(next_state.term, self.server, self)
        elif isinstance(next_state, Candidate):
            return ByzantineCandidate0(next_state.term, {}, self.server, self)
        assert(False)

    def initial_state(self) -> State:
        type_to_class = [[ByzantineCandidate0, ByzantineVoter0]]

        if self.config.server_id == 0:
            return type_to_class[self.byzantine_type][0](0, {}, self, None)
        else:
            return type_to_class[self.byzantine_type][1](0, self, None)
