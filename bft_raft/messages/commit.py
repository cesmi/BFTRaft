from typing import List

from ..config import BaseConfig
from .append_entries import AppendEntriesSuccess
from .base import ServerMessage, SignedMessage


class Cert(object):
    '''Certificate base class.'''

    def __init__(self, slot: int, incremental_hash: bytes, term: int,
                 msgs: List[SignedMessage[ServerMessage]]) -> None:
        self.slot = slot
        self.incremental_hash = incremental_hash
        self.msgs = msgs
        self.term = term

    def verify(self, config: BaseConfig) -> bool:
        if not isinstance(self.slot, int) or self.slot < 0:
            return False
        if not isinstance(self.incremental_hash, bytes):
            return False
        if not isinstance(self.msgs, list):
            return False
        if not isinstance(self.term, int) or self.term < 0:
            return False
        if len(self.msgs) < config.quorum_size:
            return False
        senders_seen = set()  # type: set
        for signed in self.msgs:
            if not isinstance(signed, SignedMessage):
                return False

            # Check that messages come from distinct servers
            sender_id = signed.sender_id
            if sender_id in senders_seen:
                return False
            senders_seen.add(sender_id)

            # Check that message is valid (signature, etc.)
            if not signed.verify(config):
                return False
        return True


class ACert(Cert):
    '''A-certificate: contains 2f + 1 AppendEntriesSuccess messages.'''

    def verify(self, config: BaseConfig) -> bool:
        '''
        Verifies that the A-Certificate is valid by checking for an acceptable
        number of messages, that all messages are signed correctly,
        that messages come from distinct servers,
        and that the AppendEntriesSuccess messages all match.'''
        if not super(ACert, self).verify(config):
            return False
        for signed in self.msgs:
            msg = signed.get_message(config)
            if not isinstance(msg, AppendEntriesSuccess):
                return False
            if not msg.incremental_hash == self.incremental_hash:
                return False
            if not msg.slot == self.slot:
                return False
        return True


class CommitMessage(ServerMessage):
    '''Sent by a replica after assembling an A-certificate.'''

    def __init__(self, sender_id: int, term: int, a_cert: ACert) -> None:
        super(CommitMessage, self).__init__(sender_id, term)
        self.a_cert = a_cert
        self.incremental_hash = a_cert.incremental_hash


class CCert(Cert):
    '''C-certificate: contains 2f + 1 commit messages.'''

    def verify(self, config: BaseConfig) -> bool:
        '''
        Verifies that the C-Certificate is valid by checking for an acceptable
        number of messages, that all messages are signed correctly,
        that messages come from distinct servers,
        and that all A-certificates are valid and match.'''
        if not super(CCert, self).verify(config):
            return False
        for signed in self.msgs:
            msg = signed.get_message(config)
            if not isinstance(msg, CommitMessage):
                return False
            if not msg.a_cert.incremental_hash == self.incremental_hash:
                return False
            if not msg.a_cert.slot == self.slot:
                return False
        return True
