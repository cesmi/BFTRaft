from .base import Message
from ..config import BaseConfig


class ClientRequest(Message):
    '''Sent by clients to request an operation be performed.'''

    def __init__(self, sender_id: int, seqno: int,
                 operation: bytes) -> None:
        super(ClientRequest, self).__init__(sender_id, True)
        self.seqno = seqno
        self.operation = operation


class ClientResponse(Message):
    '''Sent to the client after an operation is executed.'''

    def __init__(self, sender_id: int, requester: int,
                 seqno: int, result: bytes) -> None:
        super(ClientResponse, self).__init__(sender_id, False)
        self.requester = requester
        self.seqno = seqno
        self.result = result


class ClientRequestFailure(Message):
    '''Sent to the client when a request fails due to an
    outdated sequence number.'''

    def __init__(self, sender_id: int, requester: int,
                 max_seqno: int, result: bytes) -> None:
        super(ClientRequestFailure, self).__init__(sender_id, False)
        self.requester = requester
        self.max_seqno = max_seqno
        self.result = result
