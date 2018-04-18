from .base import Message


class ClientRequest(Message):
    '''Sent by clients to request an operation be performed.'''

    def __init__(self, sender_id: int, operation: str) -> None:
        super(ClientRequest, self).__init__(sender_id, True)
        self.operation = operation


class ClientResponse(Message):
    '''Sent to the client after an operation is executed.'''

    def __init__(self, sender_id: int, result: str) -> None:
        super(ClientResponse, self).__init__(sender_id, False)
        self.result = result
