from typing import Generic, TypeVar

from .hashable import Hashable
from ..config import BaseConfig

T = TypeVar('T', bound='Message')


class Message(Hashable):
    '''Base class for all messages.'''

    def __init__(self, sender_id: int, from_client: bool) -> None:
        self.sender_id = sender_id
        self.from_client = from_client

    def verify(self, config: BaseConfig) -> bool:
        '''Verifies that all fields are valid.'''
        if not isinstance(self.from_client, bool):
            return False
        if not isinstance(self.sender_id, int):
            return False
        if self.from_client:
            return self.sender_id >= 0 and self.sender_id <= config.num_clients
        return self.sender_id >= 0 and self.sender_id <= config.num_servers

    def update_hash(self, h) -> None:
        h.update(self.int_to_bytes(self.sender_id))
        h.update(bytes([self.from_client]))


class ServerMessage(Message):
    '''Base class for all messages sent between servers.'''

    def __init__(self, sender_id: int, term: int) -> None:
        super(ServerMessage, self).__init__(sender_id, False)
        self.term = term

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.term, int):
            return False
        return self.term >= 0 and super(ServerMessage, self).verify(config)

    def update_hash(self, h) -> None:
        h.update(self.int_to_bytes(self.term))
        super(ServerMessage, self).update_hash(h)


class SignedMessage(Generic[T], Hashable):
    '''A signed Message.'''

    def __init__(self, message: T, private_key) -> None:
        self.message = message
        self.signature = private_key.sign(message.hash(), '')

    def verify(self, config: BaseConfig) -> bool:
        '''Verifies the signature, deserializes the enclosed message, and
        verifies that the message is valid.'''
        if not isinstance(self.message, Message) \
                or not self.message.verify(config):
            return False
        try:
            if self.from_client:
                public_key = config.client_public_keys[self.sender_id]
            else:
                public_key = config.server_public_keys[self.sender_id]
        except KeyError:
            return False
        try:
            if not public_key.verify(self.message.hash(), self.signature):
                return False
        except TypeError:
            return False
        return True

    def update_hash(self, h) -> None:
        h.update(self.message.hash())
        for x in self.signature:
            h.update(self.int_to_bytes(x))

    @property
    def from_client(self):
        return self.message.from_client

    @property
    def sender_id(self):
        return self.message.sender_id
