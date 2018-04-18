from collections import defaultdict

from ..messages.append_entries import AppendEntriesSuccess
from ..messages.base import SignedMessage
from ..messages.client_request import ClientResponse
from ..messages.commit import ACert, CCert, CommitMessage
from .state import State


class NormalOperationBase(State):
    '''Base class for Leader and Follower states in normal operation.'''

    def __init__(self, term: int, commit_idx: int,
                 commit_idx_a_cert: ACert, copy_from: State) -> None:
        super(NormalOperationBase, self).__init__(
            copy_from.server, copy_from, term)

        # Greatest slot we know a A-cert exists for.
        self.commit_idx = commit_idx

        # The A-cert for self.commit_idx.
        self.commit_idx_a_cert = commit_idx_a_cert

        # Signed commit messages containing self.commit_idx_a_cert.
        # Map from server id to commit message.
        self.commit_messages = {}  # type: dict

        # AppendEntriesSuccess messages we have sent/received in this term for
        # slots > self.commit_idx. When we get 2f + 1 messages for a single
        # (slot, incremental hash) pair, we can increase the commit index and
        # send a commit message.
        # Map from slot number -> incremental hash -> server -> message.
        self.append_entries_success = defaultdict(dict)  # type: dict

    def on_append_entries_success(
            self, message: SignedMessage[AppendEntriesSuccess]) -> State:
        '''Called when the server receives an AppendEntriesSuccess message.'''
        if message.message.term != self.term:
            return self
        self._add_append_entries_success(message)
        return self

    def on_commit(self, message: SignedMessage[CommitMessage]) -> State:
        '''Called when the server receives a CommitMessage.'''

        # Message must be from current term
        if message.message.term != self.term:
            return self

        # If A-cert's slot number is lower than our commit index, ignore
        # the message
        a_cert = message.message.a_cert
        if self.commit_idx is not None and a_cert.slot < self.commit_idx:
            return self

        # Check the validity of the attached A-certificate
        if not a_cert.verify(self.config):
            return self

        # If the attached A-certificate's slot number is greater than our
        # commit index, increase our commit index and send out a commit
        # message
        if self.commit_idx is None or a_cert.slot > self.commit_idx:
            self._increase_commit_index(a_cert)
        assert a_cert.slot == self.commit_idx

        # Check if we now have enough commit messages to form a C-certificate.
        sender = message.message.sender_id
        self.commit_messages[sender] = message
        if len(self.commit_messages) >= self.config.quorum_size:
            commits = list(self.commit_messages.values())
            c_cert = CCert(commits[0].message.slot,
                           commits[0].message.incremental_hash,
                           commits)
            assert c_cert.verify(self.config)
            if self.applied_c_cert is None or \
                    c_cert.slot > self.applied_c_cert.slot:

                # Apply operations in log
                start = 0
                if self.applied_c_cert is not None:
                    start = self.applied_c_cert.slot + 1
                for i in range(start, c_cert.slot + 1):
                    entry = self.log[i]
                    res = self.server.application.handle_request(entry.operation,
                                                                 entry.client_id)
                    # Send response to client
                    cli_resp = ClientResponse(self.config.server_id, res)
                    self.server.messenger.send_client_message(
                        entry.client_id, cli_resp)
                self.applied_c_cert = c_cert
        return self

    def on_message(self, msg: SignedMessage) -> State:
        if isinstance(msg.message, AppendEntriesSuccess):
            return self.on_append_entries_success(msg)
        elif isinstance(msg.message, CommitMessage):
            return self.on_commit(msg)
        return super(NormalOperationBase, self).on_message(msg)

    def on_timeout(self, context: object) -> State:
        return self

    def start(self) -> None:
        raise NotImplementedError

    def _add_append_entries_success(
            self, msg: SignedMessage[AppendEntriesSuccess]) -> None:
        '''Adds msg to append_entries_success if its slot number is greater
        than the current commit index. If possible, forms a A-certificate and
        updates the current commit index.'''
        slot = msg.message.slot
        if self.commit_idx is not None and slot <= self.commit_idx:
            return

        inc_hash = msg.message.incremental_hash
        server_id = msg.message.sender_id
        self.append_entries_success[slot][inc_hash][server_id] = msg

        # Form an A-cert if possible
        num_successes = len(self.append_entries_success[slot][inc_hash])
        if num_successes >= self.config.quorum_size:
            responses = list(self.append_entries_success[slot][inc_hash].values())
            a_cert = ACert(slot, inc_hash, responses)
            self._increase_commit_index(a_cert)

    def _increase_commit_index(self, a_cert: ACert) -> None:
        '''Increases the commit index to that of the given a_cert.
        Sends a commit message to all other servers.'''
        assert self.commit_idx is None or a_cert.slot > self.commit_idx
        self.commit_idx = a_cert.slot
        self.commit_idx_a_cert = a_cert
        commit = CommitMessage(self.config.server_id,
                               self.term, a_cert)
        self.commit_messages = {self.config.server_id: commit}
        self.server.messenger.broadcast_server_message(commit)
