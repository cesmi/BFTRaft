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
        self.from_client = message.from_client
        self.sender_id = message.sender_id
        self.raw_message = pickle.dumps(message)  # type: bytes
        self.signature = private_key.sign(self.msg_hash, '')

    @property
    def msg_hash(self):
        return SHA256.new(self.raw_message).digest()

    def verify(self, public_key, config: BaseConfig) -> bool:
        return self.get_message(public_key, config) is not None

    def get_message(self, public_key, config: BaseConfig) -> T:
        '''Verifies the signature, deserializes the enclosed message, and
        verifies that the message is valid. If everything is valid, returns the
        message object. Otherwise, returns None.'''
        try:
            if not public_key.verify(self.msg_hash, self.signature):
                return None
        except TypeError:
            return None
        try:
            msg = pickle.loads(self.raw_message)
        except pickle.UnpicklingError:
            return None
        if not isinstance(msg, Message) or not msg.verify(config):
            return None
        return msg  # type: ignore
