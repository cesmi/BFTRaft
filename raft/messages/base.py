

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
