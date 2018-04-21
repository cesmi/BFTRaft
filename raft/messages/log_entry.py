from typing import List

from ..config import BaseConfig
from .client_request import ClientRequest


class LogEntry(object):
    def __init__(self, term: int,
                 client_request: ClientRequest) -> None:
        self.term = term
        self.request = client_request

    @property
    def client_id(self):
        return self.request.sender_id

    @property
    def seqno(self):
        return self.request.seqno

    @property
    def operation(self):
        return self.request.operation
