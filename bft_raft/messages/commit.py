from typing import List

from ..config import ServerConfig
from .append_entries import AppendEntriesSuccess
from .base import ServerMessage, SignedMessage


class Cert(object):
    '''Certificate base class.'''

    def verify(self, config: ServerConfig) -> bool:
        if(len(self.responses) != config.quorum_size):
            return False
        senders_seen = set()
        hash_to_match = self.responses[0].incremental_hash
        for response in self.responses:
            sender_id = response.sender_id
            public_key = config.server_public_keys[sender_id]
            # Check that messages come from distinct servers
            if sender_id in senders_seen:
                return False
            senders_seen.add(sender_id)
            # Check that message is signed correctly
            if not response.verify(public_key):
                return False
            # Check that all hashes match
            if response.incremental_hash != hash_to_match:
                return False
        return True


class ACert(Cert):
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
        number of messages, that all messages are signed correctly,
        that messages come from distinct servers,
        and that the AppendEntriesSuccess messages all match.'''
        super(ACert, self).verify(config)


class CommitMessage(ServerMessage):
    '''Sent by a replica after assembling an A-certificate.'''

    def __init__(self, sender_id: int, term: int, a_cert: ACert) -> None:
        super(CommitMessage, self).__init__(sender_id, term)
        self.a_cert = a_cert
        self.incremental_hash = a_cert.incremental_hash


class CCert(Cert):
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
        number of messages, that all messages are signed correctly,
        that messages come from distinct servers,
        and that all A-certificates are valid and match.'''

        for response in self.responses:
            # Check that A certificates are valid
            if not response.a_cert.verify(config):
                return False
        return super(CCert, self).verify(config)
