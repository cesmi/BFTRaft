from ..config import ServerConfig
from ..messages.base import SignedMessage
from ..messages.commit import CCert  # pylint:disable=W0611
from ..servers.base import BaseServer
from .abstract import AbstractState


class State(AbstractState):
    def __init__(self, server: BaseServer, copy_from: State = None,
                 term: int = None) -> None:
        self.server = server
        self.log = []  # type: list
        self.term = 0
        self.applied_c_cert = None  # type: CCert

        if copy_from is not None:
            self.log = copy_from.log
            self.term = copy_from.term
            self.applied_c_cert = copy_from.applied_c_cert

        if term is not None:
            self.term = term

    def start(self):
        raise NotImplementedError

    def on_message(self, msg: SignedMessage) -> State:
        if msg.message.term != self.term:
            # TODO: Possibly add a request for proof of view change
            return self
        return self

    def on_timeout(self, context: object) -> State:
        return self

    @property
    def config(self) -> ServerConfig:
        return self.server.config
