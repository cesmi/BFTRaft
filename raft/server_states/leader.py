from collections import defaultdict
from typing import Dict, Set  # pylint:disable=W0611

from ..messages import (AppendEntriesRequest, AppendEntriesResponse,
                        ClientRequest, ClientRequestFailure, ClientResponse,
                        LogEntry)
from ..servers.base import BaseServer
from .state import State


class Leader(State):
    def __init__(self, term: int, copy_from: State = None,
                 server: BaseServer = None) -> None:
        super(Leader, self).__init__(server, copy_from, term)
        self._send_heartbeat()

        # map from slot to set of server ids
        self._successes = defaultdict(set)  # type: Dict[int, Set[int]]

    def on_client_request(self, msg: ClientRequest):
        entry = LogEntry(self.term, msg)

        # Build an AppendEntriesRequest to send to other servers
        request = AppendEntriesRequest(self.config.server_id, self.term,
                                       self._prev_slot, self._prev_term, [entry],
                                       self.commit_idx)
        self.log.append(entry)
        self._successes[len(self.log) - 1].add(self.config.server_id)
        self.server.messenger.broadcast_server_message(request)
        return self

    def on_append_entries_response(self, msg: AppendEntriesResponse):
        if msg.term != self.term:
            return self
        if msg.success and (self.commit_idx is None or msg.slot > self.commit_idx):
            self._successes[msg.slot].add(msg.sender_id)
            if len(self._successes[msg.slot]) >= self.config.quorum_size:
                self.update_commit_idx(msg.slot)
        elif not msg.success:
            assert msg.slot < len(self.log)
            prev_slot = msg.slot - 1 if msg.slot > 0 else None
            prev_term = self.log[msg.slot - 1].term if msg.slot > 0 else None
            new_req = AppendEntriesRequest(self.config.server_id, self.term,
                                           prev_slot, prev_term,
                                           self.log[prev_slot + 1:],
                                           self.commit_idx)
            self.server.messenger.send_server_message(msg.sender_id, new_req)
        return self

    def on_timeout(self, context: object) -> State:
        if isinstance(context, LeaderHeartbeatTimeout):
            self._send_heartbeat()
            return self
        else:
            return super(Leader, self).on_timeout(context)

    def update_commit_idx(self, commit_idx: int) -> None:
        super(Leader, self).update_commit_idx(commit_idx)
        for slot in list(self._successes.keys()):
            if slot <= commit_idx:
                del self._successes[slot]

    def execute_entry(self, slot: int) -> bytes:
        result = super(Leader, self).execute_entry(slot)
        entry = self.log[slot]
        client_id = self.log[slot].client_id

        resp = None  # type: ignore
        if result is not None:
            resp = ClientResponse(self.config.server_id, client_id,
                                  entry.seqno, result)
        else:
            assert client_id in self.latest_req_per_client
            resp = ClientRequestFailure(  # type: ignore
                self.config.server_id, client_id,
                self.latest_req_per_client[client_id][0],
                self.latest_req_per_client[client_id][1])
        self.server.messenger.send_client_message(client_id, resp)
        return result

    def _send_heartbeat(self):
        self.server.timeout_manager.set_timeout(
            self.config.timeout / 2, LeaderHeartbeatTimeout())
        msg = AppendEntriesRequest(self.config.server_id, self.term,
                                   self._prev_slot, self._prev_term,
                                   [], self.commit_idx)
        self.server.messenger.broadcast_server_message(msg)

    @property
    def _prev_slot(self) -> int:
        return len(self.log) - 1 if self.log else None

    @property
    def _prev_term(self) -> int:
        return self.log[-1].term if self.log else None


class LeaderHeartbeatTimeout(object):
    pass
