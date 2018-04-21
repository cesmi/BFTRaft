import random
import time

from ..messages import AppendEntriesRequest
from ..servers.base import BaseServer
from .state import State


class Follower(State):
    def __init__(self, term: int, copy_from: State = None,
                 server: BaseServer = None) -> None:
        super(Follower, self).__init__(server, copy_from, term)
        self.last_append_entries_time = time.time()
        self.random_timeout = self.get_random_timeout()
        self.server.timeout_manager.set_timeout(
            self.config.timeout, FollowerHeartbeatTimeout())

    def on_append_entries_request(self, msg: AppendEntriesRequest) -> State:
        # update last heartbeat time
        if msg.term == self.term:
            self.last_append_entries_time = time.time()
            self.random_timeout = self.get_random_timeout()
        return super(Follower, self).on_append_entries_request(msg)

    def on_timeout(self, context: object) -> State:
        if isinstance(context, FollowerHeartbeatTimeout):
            return self.on_heartbeat_timeout()
        else:
            return super(Follower, self).on_timeout(context)

    def on_heartbeat_timeout(self) -> State:
        from .candidate import Candidate
        if time.time() - self.last_append_entries_time > self.random_timeout:
            self.config.log('Timed out, becoming candidate for term %d' % (self.term + 1))
            new_state = Candidate(self.term + 1, self)
            new_state.send_vote_request()
            return new_state
        else:
            self.server.timeout_manager.set_timeout(
                self.config.timeout, FollowerHeartbeatTimeout())
            return self

    def get_random_timeout(self) -> float:
        return random.uniform(self.config.timeout,
                              self.config.timeout * 2)


class FollowerHeartbeatTimeout(object):
    pass
