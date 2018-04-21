from .base import ServerMessage


class VoteMessage(ServerMessage):
    pass  # nothing needed here


class VoteRequest(ServerMessage):
    '''Sent by a candidate to clients after receiving f + 1
    votes (i.e. at least 1 vote from a correct server).'''

    def __init__(self, sender_id: int, term: int,
                 last_log_index: int, last_log_term: int) -> None:
        super(VoteRequest, self).__init__(sender_id, term)
        self.last_log_index = last_log_index
        self.last_log_term = last_log_term
