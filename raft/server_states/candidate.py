from ..messages import VoteMessage, VoteRequest
from ..servers.base import BaseServer
from .state import State


class Candidate(State):
    def __init__(self, term: int, copy_from: State = None,
                 server: BaseServer = None) -> None:
        super(Candidate, self).__init__(server, copy_from, term)
        # Add a vote from ourself
        self.votes = set([self.config.server_id])
        self.send_vote_request()

    def send_vote_request(self):
        last_log_index = None  # type: int
        last_log_term = None  # type: int
        if self.log:
            last_log_index = len(self.log) - 1
            last_log_term = self.log[-1].term
        req = VoteRequest(self.config.server_id, self.term,
                          last_log_index, last_log_term)
        self.server.messenger.broadcast_server_message(req)
        self.server.timeout_manager.set_timeout(self.config.timeout / 2,
                                                VoteResendTimeout())

    def on_vote(self, msg: VoteMessage) -> State:
        from .leader import Leader
        if msg.term != self.term:
            return self
        self.votes.add(msg.sender_id)

        # If have a quorum of votes, we are now elected
        if len(self.votes) >= self.config.quorum_size:
            self.config.log(
                'Received quorum of votes for term %d, becoming leader' % self.term)
            return Leader(self.term, self)
        return self

    def on_timeout(self, context: object):
        if isinstance(context, VoteResendTimeout):
            self.send_vote_request()
            return self
        return super(Candidate, self).on_timeout(context)


class VoteResendTimeout(object):
    pass
