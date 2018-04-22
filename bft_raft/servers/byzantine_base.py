from ..application import Application
from ..config import ServerConfig
from ..messages import Message, SignedMessage
from ..messengers.listener import MessengerListener
from ..messengers.messenger import Messenger
from ..server_states.state import State
from ..timeout_managers.listener import TimeoutListener
from ..timeout_managers.timeout_manager import TimeoutManager

from .base import BaseServer

class ByzantineBaseServer(BaseServer):
    def __init__(self, config: ServerConfig, application: Application,
                 messenger: Messenger, timeout_manager: TimeoutManager,
                 byzantine_type: int) -> None:
        self.byzantine_type = byzantine_type
        super(ByzantineBaseServer, self).__init__(config, application, 
                messenger, timeout_manager)

    def on_message(self, msg: Message, signed: SignedMessage) -> None:
        return super(ByzantineBaseServer, self).on_message(msg, signed)

    def on_timeout(self, context: object) -> None:
        return super(ByzantineBaseServer, self).on_timeout(context)

    def initial_state(self) -> State:
        from ..server_states.byzantine_candidate import ByzantineCandidate0
        from ..server_states.byzantine_voter import ByzantineVoter0
        from ..server_states.byzantine_follower import ByzantineFollower0
        from ..server_states.byzantine_leader import ByzantineLeader0

        type_to_class = [[ByzantineCandidate0, ByzantineVoter0]]

        if self.config.server_id == 0:
            return type_to_class[self.byzantine_type][0](0, {}, self, None)
        else:
            return type_to_class[self.byzantine_type][1](0, self, None)
