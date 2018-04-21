from ..application import Application
from ..config import ServerConfig
from ..messages import Message
from ..messengers.listener import MessengerListener
from ..messengers.messenger import Messenger
from ..server_states.state import State
from ..timeout_managers.listener import TimeoutListener
from ..timeout_managers.timeout_manager import TimeoutManager


class BaseServer(MessengerListener, TimeoutListener):
    def __init__(self, config: ServerConfig, application: Application,
                 messenger: Messenger, timeout_manager: TimeoutManager) -> None:
        self.config = config
        self.application = application
        self.messenger = messenger
        self.timeout_manager = timeout_manager
        messenger.add_listener(self)
        timeout_manager.add_listener(self)
        self.state = self.initial_state()

    def on_message(self, msg: Message) -> None:
        self.state = self.state.on_message(msg)

    def on_timeout(self, context: object) -> None:
        self.state = self.state.on_timeout(context)

    def initial_state(self) -> State:
        from ..server_states.candidate import Candidate
        from ..server_states.follower import Follower
        if self.config.server_id == 0:
            return Candidate(0, None, self)
        else:
            return Follower(0, None, self)
