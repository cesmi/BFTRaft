from ..config import BaseConfig
from ..messages import Message, ServerMessage, SignedMessage
from .messenger import Messenger


class SentMessage(object):
    class Type(object):
        TO_CLIENT = 0
        TO_SERVER = 1
        TO_ALL_SERVERS = 2

    def __init__(self, send_type: int, recipient: int,
                 message: Message, signed: SignedMessage) -> None:
        self.send_type = send_type
        self.recipient = recipient
        self.message = message
        self.signed = signed


class MemoryQueueMessenger(Messenger):
    '''Stores sent messages in a queue instead of sending them over the network.
    Used for testing.'''

    def __init__(self, config: BaseConfig) -> None:
        super(MemoryQueueMessenger, self).__init__(config)
        self.sent = []  # type: ignore

    def get_message(self) -> SentMessage:
        '''Pops message off the front of the sent queue and returns it.'''
        if not self.sent:
            return None
        rval = self.sent[0]
        self.sent = self.sent[1:]
        return rval

    def send_server_message(self, server_id: int, message: ServerMessage) -> None:
        self.sent.append(SentMessage(
            SentMessage.Type.TO_SERVER, server_id, message, self._sign(message)))

    def send_client_message(self, client_id: int, message: Message) -> None:
        self.sent.append(SentMessage(
            SentMessage.Type.TO_CLIENT, client_id, message, self._sign(message)))

    def broadcast_server_message(self, message) -> None:
        self.sent.append(SentMessage(
            SentMessage.Type.TO_ALL_SERVERS, None, message, self._sign(message)))

    def _sign(self, message: Message) -> SignedMessage:
        return SignedMessage(message, self.config.private_key)
