from typing import Dict, List, Tuple, TypeVar  # pylint:disable=W0611

from ..config import ServerConfig
from ..messages import (AppendEntriesRequest, AppendEntriesResponse,
                        ClientRequest, ClientResponse, ClientRequestFailure,
                        LogEntry, Message, VoteMessage, VoteRequest)

if False:  # pylint:disable=W0125
    # (just for type checking; if statement avoids circular import)
    from ..servers.base import BaseServer  # pylint:disable=W0611


class State(object):
    def __init__(self, server: 'BaseServer', copy_from: 'State' = None,
                 term: int = None) -> None:
        if server is None:
            assert copy_from is not None
            server = copy_from.server

        self.server = server  # type: BaseServer
        self.log = []  # type: List[LogEntry]
        self.term = 0
        self.voted_for = None  # type: int
        self.commit_idx = None  # type: int

        # Map from client id to (seqno, result) pair for the request with
        # greatest sequence number executed by a client.
        self.latest_req_per_client = {}  # type: Dict[int, Tuple[int, bytes]]

        if copy_from is not None:
            self.log = copy_from.log
            self.term = copy_from.term
            self.latest_req_per_client = copy_from.latest_req_per_client
            self.voted_for = copy_from.voted_for
            self.commit_idx = copy_from.commit_idx
        if term is not None:
            assert term >= self.term
            self.term = term
            self.voted_for = None

    def on_message(self, msg: Message) -> 'State':
        '''Invokes the appropriate callback for msg. Returns resulting state.'''
        if isinstance(msg, AppendEntriesRequest):
            return self.on_append_entries_request(msg)
        elif isinstance(msg, AppendEntriesResponse):
            return self.on_append_entries_response(msg)
        elif isinstance(msg, ClientRequest):
            return self.on_client_request(msg)
        elif isinstance(msg, VoteMessage):
            return self.on_vote(msg)
        elif isinstance(msg, VoteRequest):
            return self.on_vote_request(msg)
        else:
            assert False, 'unhandled message type %s' % msg.__class__.__name__

    def on_append_entries_request(self, msg: AppendEntriesRequest) -> 'State':
        from .follower import Follower

        # request proof of election if sender claims higher term
        if msg.term < self.term:
            return self
        resp = None  # type: ignore

        # Must have matching entry at prev_log_index
        if msg.prev_log_index is not None and (
            len(self.log) - 1 < msg.prev_log_index
                or self.log[msg.prev_log_index].term != msg.prev_log_term):
            resp = AppendEntriesResponse(self.config.server_id, msg.term,
                                         msg.prev_log_index, success=False)
        elif msg.entries:  # not a heartbeat
            # on success, append the entries to our log
            keep_end = msg.prev_log_index + 1 if msg.prev_log_index is not None else 0
            self.log = self.log[:keep_end] + msg.entries
            resp = AppendEntriesResponse(self.config.server_id, msg.term,
                                         len(self.log) - 1, success=True)
        if resp is not None:
            self.server.messenger.send_server_message(msg.sender_id, resp)

        if msg.leader_commit is not None:
            if self.commit_idx is None or self.commit_idx < msg.leader_commit:
                self.update_commit_idx(msg.leader_commit)
        if self.term < msg.term:
            return Follower(msg.term, self)
        return self

    def on_append_entries_response(self, msg: AppendEntriesResponse) -> 'State':
        return self

    def on_client_request(self, msg: ClientRequest) -> 'State':
        return self

    def on_vote(self, msg: VoteMessage) -> 'State':
        return self

    def on_vote_request(self, msg: VoteRequest) -> 'State':
        from .follower import Follower

        if msg.term < self.term:
            return self
        if self.voted_for is not None and self.voted_for != msg.sender_id:
            return self

        # candidate's log must be at least as up to date as ours
        if msg.last_log_index is None:
            assert msg.last_log_term is None
            if self.log:  # not empty
                return self
        else:
            if len(self.log) - 1 > msg.last_log_index:
                return self
            if self.log and self.log[-1].term >= msg.term:
                assert self.log[-1].term > msg.term
                return self

        # send vote and become a follower
        vote = VoteMessage(self.config.server_id, msg.term)
        self.server.messenger.send_server_message(msg.sender_id, vote)
        return Follower(msg.term, self)

    def on_timeout(self, context: object) -> 'State':
        '''Returns resulting state.'''
        return self

    def update_commit_idx(self, commit_idx: int) -> None:
        assert commit_idx is not None
        assert self.commit_idx is None or commit_idx > self.commit_idx
        assert len(self.log) > commit_idx
        start = 0 if self.commit_idx is None else self.commit_idx
        for i in range(start, commit_idx + 1):
            self.execute_entry(i)
        self.commit_idx = commit_idx

    def execute_entry(self, slot: int) -> bytes:
        entry = self.log[slot]
        client_id = entry.client_id

        # Check that sequence number is > than the max used for this client
        if client_id in self.latest_req_per_client \
                and self.latest_req_per_client[client_id][0] >= entry.seqno:
            return None
        else:
            result = self.server.application.handle_request(
                entry.operation, entry.client_id)
            self.latest_req_per_client[client_id] = (entry.seqno, result)
            return result

    @property
    def config(self) -> ServerConfig:
        return self.server.config
