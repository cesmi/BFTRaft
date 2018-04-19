from .base import Message
from ..config import BaseConfig


class ClientRequest(Message):
    '''Sent by clients to request an operation be performed.'''

    def __init__(self, sender_id: int, operation: bytes) -> None:
        super(ClientRequest, self).__init__(sender_id, True)
        self.operation = operation

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.operation, bytes):
            return False
        return super(ClientRequest, self).verify(config)


class ClientResponse(Message):
    '''Sent to the client after an operation is executed.'''

    def __init__(self, sender_id: int, result: str) -> None:
        super(ClientResponse, self).__init__(sender_id, False)
        self.result = result

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.result, bytes):
            return False
        return super(ClientResponse, self).verify(config)
