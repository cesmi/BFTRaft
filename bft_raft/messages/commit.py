from typing import List

from ..config import ServerConfig
from .append_entries import AppendEntriesSuccess
from .base import ServerMessage, SignedMessage


class ACert(object):
    '''A-certificate: contains 2f + 1 AppendEntriesSuccess messages.'''

    def __init__(
            self, slot: int, incremental_hash: bytes,
            responses: List[SignedMessage[AppendEntriesSuccess]]) -> None:
        self.slot = slot
        self.incremental_hash = incremental_hash
        self.responses = responses

    def verify(self, config: ServerConfig) -> bool:
        '''
        Verifies that the A-Certificate is valid by checking for an acceptable
        number of messages, that all messages are signed correctly, that messages
        come from distinct servers, and that the AppendEntriesSuccess messages
        all match.'''
        return True  # TODO


class CommitMessage(ServerMessage):
    '''Sent by a replica after assembling an A-certificate.'''

    def __init__(self, sender_id: int, term: int, a_cert: ACert) -> None:
        super(CommitMessage, self).__init__(sender_id, term)
        self.a_cert = a_cert


class CCert(object):
    '''C-certificate: contains 2f + 1 commit messages.'''

    def __init__(
            self, slot: int, incremental_hash: bytes,
            commits: List[SignedMessage[CommitMessage]]) -> None:
        self.slot = slot
        self.incremental_hash = incremental_hash
        self.responses = commits

    def verify(self, config: ServerConfig) -> bool:
        '''
        Verifies that the C-Certificate is valid by checking for an acceptable
        number of messages, that all messages are signed correctly, that messages
        come from distinct servers, and that all A-certificates are
        valid and match.'''
        return True  # TODO
