import pickle
from typing import Generic, TypeVar

from Crypto.Hash import SHA256
from ..config import BaseConfig

T = TypeVar('T', bound='Message')


class Message(object):
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
        else:
            return self.sender_id >= 0 and self.sender_id <= config.num_servers


class ServerMessage(Message):
    '''Base class for all messages sent between servers.'''

    def __init__(self, sender_id: int, term: int) -> None:
        super(ServerMessage, self).__init__(sender_id, False)
        self.term = term

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.term, int):
            return False
        return self.term >= 0 and super(ServerMessage, self).verify(config)


class SignedMessage(Generic[T]):
    '''A signed Message.'''

    def __init__(self, message: T, private_key) -> None:
        self.message = message  # type: T
        msg_hash = SHA256.new(pickle.dumps(message)).digest()
        self.signature = private_key.sign(msg_hash, '')  # type: bytes

    def verify(self, public_key, config: BaseConfig) -> bool:
        '''Verifies the message signature with given public key, and
        verifies the enclosed message.'''
        if not isinstance(self.message, Message):
            return False
        if not isinstance(self.signature, bytes):
            return False
        msg_hash = SHA256.new(pickle.dumps(self.message)).digest()
        return public_key.verify(msg_hash, self.signature) \
            and self.message.verify(config)
