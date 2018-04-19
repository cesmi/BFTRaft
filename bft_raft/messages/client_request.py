from .base import Message
from ..config import BaseConfig


class ClientRequest(Message):
    '''Sent by clients to request an operation be performed.'''

    def __init__(self, sender_id: int, seqno: int,
                 operation: bytes) -> None:
        super(ClientRequest, self).__init__(sender_id, True)
        self.seqno = seqno
        self.operation = operation

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.operation, bytes):
            return False
        if not isinstance(self.seqno, int) or self.seqno < 0:
            return False
        return super(ClientRequest, self).verify(config)

    def update_hash(self, h) -> None:
        h.update(self.int_to_bytes(self.seqno))
        h.update(self.operation)
        super(ClientRequest, self).update_hash(h)


class ClientResponse(Message):
    '''Sent to the client after an operation is executed.'''

    def __init__(self, sender_id: int, requester: int,
                 seqno: int, result: bytes) -> None:
        super(ClientResponse, self).__init__(sender_id, False)
        self.requester = requester
        self.seqno = seqno
        self.result = result

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.requester, int) or self.requester < 0:
            return False
        if not isinstance(self.seqno, int) or self.seqno < 0:
            return False
        if not isinstance(self.result, bytes):
            return False
        return super(ClientResponse, self).verify(config)

    def update_hash(self, h) -> None:
        h.update(self.int_to_bytes(self.requester))
        h.update(self.int_to_bytes(self.seqno))
        h.update(self.result)
        super(ClientResponse, self).update_hash(h)


class ClientRequestFailure(Message):
    '''Sent to the client when a request fails due to an
    outdated sequence number.'''

    def __init__(self, sender_id: int, requester: int,
                 max_seqno: int, result: bytes) -> None:
        super(ClientRequestFailure, self).__init__(sender_id, False)
        self.requester = requester
        self.max_seqno = max_seqno
        self.result = result

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.requester, int) or self.requester < 0:
            return False
        if not isinstance(self.max_seqno, int) or self.max_seqno < 0:
            return False
        if not isinstance(self.result, bytes):
            return False
        return super(ClientRequestFailure, self).verify(config)

    def update_hash(self, h) -> None:
        h.update(self.int_to_bytes(self.requester))
        h.update(self.int_to_bytes(self.max_seqno))
        h.update(self.result)
        super(ClientRequestFailure, self).update_hash(h)
