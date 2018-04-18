import pickle
from typing import Generic, TypeVar

from Crypto.Hash import SHA256

T = TypeVar('T', bound='Message')


class Message(object):
    '''Base class for all messages.'''

    def __init__(self, sender_id: int, from_client: bool) -> None:
        self.sender_id = sender_id
        self.from_client = from_client


class ServerMessage(Message):
    '''Base class for all messages sent between servers.'''

    def __init__(self, sender_id: int, term: int) -> None:
        super(ServerMessage, self).__init__(sender_id, False)
        self.term = term


class SignedMessage(Generic[T]):
    '''A signed Message.'''

    def __init__(self, message: T, private_key) -> None:
        self.message = message  # type: T
        msg_hash = SHA256.new(pickle.dumps(message)).digest()
        self.signature = private_key.sign(msg_hash, '')  # type: bytes

    def verify(self, public_key) -> bool:
        '''Verifies the message signature with given public key.'''
        msg_hash = SHA256.new(pickle.dumps(self.message)).digest()
        return public_key.verify(msg_hash, self.signature)
