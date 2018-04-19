from ..application import Application
from ..config import ServerConfig
from ..messages import SignedMessage
from ..messengers import Messenger, MessengerListener
from ..server_states import State
from ..timeout_managers import TimeoutManager, TimeoutListener


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
        self.state.start()

    def on_message(self, message: SignedMessage) -> None:
        self.state = self.state.on_message(message)

    def on_timeout(self, context: object) -> None:
        self.state = self.state.on_timeout(context)

    def initial_state(self) -> State:
        from ..server_states import Candidate, Voter
        if self.config.server_id == 0:
            return Candidate(0, {}, self, None)
        else:
            return Voter(0, self, None)
