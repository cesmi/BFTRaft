from ..config import BaseConfig
from ..messages import Message, ServerMessage, SignedMessage
from .messenger import Messenger


class SendType(object):
    TO_CLIENT = 0
    TO_SERVER = 1
    TO_ALL_SERVERS = 2


class MemoryQueueMessenger(Messenger):
    '''Stores sent messages in a queue instead of sending them over the network.
    Used for testing.'''

    def __init__(self, config: BaseConfig) -> None:
        super(MemoryQueueMessenger, self).__init__(config)
        self.sent = []  # type: ignore

    def get_message(self):
        '''Pops message off the front of the sent queue and returns it.'''
        if not self.sent:
            return None
        rval = self.sent[0]
        self.sent = self.sent[1:]
        return rval

    def send_server_message(self, server_id: int, message: ServerMessage) -> None:
        self.sent.append((SendType.TO_SERVER, server_id, self._sign(message)))

    def send_client_message(self, client_id: int, message: Message) -> None:
        self.sent.append((SendType.TO_CLIENT, client_id, self._sign(message)))

    def broadcast_server_message(self, message) -> None:
        self.sent.append((SendType.TO_ALL_SERVERS, None, self._sign(message)))

    def _sign(self, message: Message):
        return SignedMessage(message, self.config.private_key)
