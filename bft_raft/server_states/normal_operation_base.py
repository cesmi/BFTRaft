from collections import defaultdict

from ..messages import (ACert, AppendEntriesSuccess, CCert, ClientResponse,
                        CommitMessage, SignedMessage)
from .state import State


class NormalOperationBase(State):
    '''Base class for Leader and Follower states in normal operation.'''

    def __init__(self, term: int, copy_from: State) -> None:
        super(NormalOperationBase, self).__init__(
            copy_from.server, copy_from, term)

        # Signed commit messages containing self.latest_a_cert.
        # Map from server id to commit message.
        # When we get 2f + 1 matching messages we can form a CCert and apply
        # log entries.
        self.commit_messages = {}  # type: dict

        # AppendEntriesSuccess messages we have sent/received in this term for
        # slots > self.latest_a_cert.slot. When we get 2f + 1 messages for a
        # single (slot, incremental hash) pair, we can increase the commit
        # index and send a commit message.
        # Map from slot number -> incremental hash -> server -> message.
        self.append_entries_success = defaultdict(dict)  # type: dict

        # Commit messages we have received in this term for
        # slots > self.latest_a_cert.slot.
        # Map from slot number -> server -> message.
        self.future_commits = defaultdict(dict)  # type: dict

    def on_append_entries_success(self, msg: AppendEntriesSuccess,
                                  signed: SignedMessage[AppendEntriesSuccess]) -> State:
        if msg.term != self.term:
            if msg.term > self.term:
                self._request_election_proof(msg.term)
            return self
        self._add_append_entries_success(signed)
        return self

    def on_commit(self, msg: CommitMessage,
                  signed: SignedMessage[CommitMessage]) -> State:

        # Message must be from current term
        if msg.term != self.term:
            if msg.term > self.term:
                self._request_election_proof(msg.term)
            return self

        # If A-cert's slot number is lower than that of our latest a-cert, ignore
        # the message
        a_cert = msg.a_cert
        if self.latest_a_cert is not None and \
                a_cert.slot < self.latest_a_cert.slot:
            return self

        # If the attached A-certificate's slot number is greater than that of our
        # latest a-cert, save it in self.future_commits
        if self.latest_a_cert is None or a_cert.slot > self.latest_a_cert.slot:
            self.future_commits[a_cert.slot][msg.sender_id] = signed
            return self

        # If we make it here the a_cert must have equal slot to our latest a-cert
        assert self.latest_a_cert.slot == a_cert.slot
        self._add_commit(signed)
        return self

    def on_timeout(self, context: object) -> State:
        return self

    def start(self) -> None:
        raise NotImplementedError

    def _add_append_entries_success(
            self, msg: SignedMessage[AppendEntriesSuccess]) -> None:
        '''Adds msg to append_entries_success if its slot number is greater
        than the that of our latest a-cert. If possible, forms a A-cert and
        updates the current commit index.'''
        slot = msg.message.slot
        if self.latest_a_cert.slot is not None \
                and slot <= self.latest_a_cert.slot:
            return

        inc_hash = msg.message.incremental_hash
        server_id = msg.message.sender_id
        self.append_entries_success[slot][inc_hash][server_id] = msg

        # Form an A-cert if possible
        num_successes = len(self.append_entries_success[slot][inc_hash])
        if num_successes >= self.config.quorum_size \
                and self.config.server_id in self.append_entries_success[slot][inc_hash]:
            responses = list(
                self.append_entries_success[slot][inc_hash].values())
            new_a_cert = ACert(slot, inc_hash, self.term, responses)
            assert new_a_cert.verify(self.config)
            self._a_cert_formed(new_a_cert)

    def _add_commit(
            self, signed: SignedMessage[CommitMessage]) -> None:
        '''Adds a commit message with slot equal to that of our latest A-cert
        to self.commit_messages.'''
        msg = signed.message
        assert msg.a_cert.slot == self.latest_a_cert.slot
        self.commit_messages[msg.sender_id] = signed

        # Check if we now have enough commit messages to form a C-certificate.
        if len(self.commit_messages) >= self.config.quorum_size:
            commits = list(self.commit_messages.values())
            c_cert = CCert(commits[0].message.slot,
                           commits[0].message.incremental_hash,
                           self.term, commits)
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

    def _a_cert_formed(self, a_cert: ACert) -> None:
        '''Called when we get enough AppendEntriesSuccess messgaes to form
        an A-cert. Sends a commit message to all other servers.'''
        assert self.latest_a_cert is None \
            or a_cert.slot > self.latest_a_cert.slot
        self.latest_a_cert = a_cert

        # broadcast commit message
        commit = CommitMessage(self.config.server_id, self.term, a_cert)
        self.server.messenger.broadcast_server_message(commit)

        # find all commit messages that we have with this slot
        self.commit_messages = {}
        self._add_commit(SignedMessage(commit, self.config.private_key))
        assert self.config.server_id not in self.future_commits[a_cert.slot]
        for c in self.future_commits[a_cert.slot].values():
            assert c.a_cert.verify(self.config)
            self._add_commit(c)

        # clean up self.future_commits
        for slot in self.future_commits.keys():
            if slot <= a_cert.slot:
                del self.future_commits[slot]

        # Clean up self.append_entries_success
        for slot in self.append_entries_success.keys():
            if slot <= a_cert.slot:
                del self.append_entries_success[slot]
