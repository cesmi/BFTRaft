from ..application import Application
from ..config import ServerConfig
from ..messages.base import SignedMessage
from ..messenger.base import Messenger
from ..messenger.listener import MessengerListener
from ..states.abstract import AbstractState
from ..timeout_manager.base import TimeoutManager
from ..timeout_manager.listener import TimeoutListener


class BaseServer(MessengerListener, TimeoutListener):
    def __init__(self, config: ServerConfig, application: Application,
                 messenger: Messenger, timeout_manager: TimeoutManager) -> None:
        self.config = config
        self.application = application
        self.messenger = messenger
        self.timeout_manager = timeout_manager
        messenger.add_listener(self)
        timeout_manager.add_listener(self)

        self.state = None  # type: AbstractState
        if self.config.server_id == 0:
            self.state = AbstractState()
        else:
            self.state = AbstractState()
        self.state.start()

    def on_message(self, message: SignedMessage) -> None:
        self.state = self.state.on_message(message)

    def on_timeout(self, context: object) -> None:
        self.state = self.state.on_timeout(context)
