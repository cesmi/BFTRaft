from typing import Dict, List  # pylint:disable=W0611
from ..config import ServerConfig
from ..log_entry import LogEntry  # pylint:disable=W0611
from ..messages import CCert  # pylint:disable=W0611
from ..messages import (AppendEntriesRequest, AppendEntriesSuccess, ClientRequest,
                        ClientResponse, CommitMessage, ElectedMessage,
                        SignedMessage, VoteMessage, VoteRequest)

if False:  # pylint:disable=W0125
    # (just for type checking; if statement avoids circular import)
    from ..servers import BaseServer


class State(object):
    def __init__(self, server: BaseServer, copy_from: State = None,
                 term: int = None) -> None:
        self.server = server
        self.log = []  # type: List[LogEntry]
        self.term = 0
        self.applied_c_cert = None  # type: CCert

        # Votes received by this server.
        # Map from term id to server id to signed vote message.
        self.votes = {}  # type: Dict[int, Dict[int, SignedMessage[VoteMessage]]]

        if copy_from is not None:
            self.log = copy_from.log
            self.term = copy_from.term
            self.applied_c_cert = copy_from.applied_c_cert

        if term is not None:
            self.term = term

    @classmethod
    def initial_state(cls, config: ServerConfig):
        pass

    def start(self):
        '''Performs any actions a server in this state should perform on startup.'''
        raise NotImplementedError

    def on_message(self, msg: SignedMessage) -> State:
        '''Invokes the appropriate callback for msg. Returns resulting state.'''
        m = msg.message  # unsigned
        if isinstance(m, AppendEntriesRequest):
            return self.on_append_entries_request(m, msg)
        elif isinstance(m, AppendEntriesSuccess):
            return self.on_append_entries_success(m, msg)
        elif isinstance(m, ClientRequest):
            return self.on_client_request(m, msg)
        elif isinstance(m, ClientResponse):
            return self.on_client_response(m, msg)
        elif isinstance(m, CommitMessage):
            return self.on_commit(m, msg)
        else:
            assert False, 'unhandled message type'

    def on_append_entries_request(self, msg: AppendEntriesRequest,
                                  signed: SignedMessage[AppendEntriesRequest]) -> State:
        return self

    def on_append_entries_success(self, msg: AppendEntriesSuccess,
                                  signed: SignedMessage[AppendEntriesSuccess]) -> State:
        return self

    def on_client_request(self, msg: ClientRequest,
                          signed: SignedMessage[ClientRequest]) -> State:
        return self

    def on_client_response(self, msg: ClientResponse,
                           signed: SignedMessage[ClientResponse]) -> State:
        return self

    def on_commit(self, msg: CommitMessage,
                  signed: SignedMessage[CommitMessage]) -> State:
        return self

    def on_vote(self, msg: VoteMessage,
                signed: SignedMessage[VoteMessage]) -> State:
        # Add vote to votes map if term > current term
        # If have >= f + 1 votes, one must be from a correct replica,
        # so send a vote request to all replicas and transition to
        # candidate state
        pass

    def on_vote_request(self, msg: VoteRequest,
                        signed: SignedMessage[VoteRequest]) -> State:

        # Send a vote if proof of f + 1 votes is valid and votes are for
        # future term
        if not msg.verify(self.config):
            return self
        if msg.term <= self.term:
            return self
        # TODO: Return Voter
        return self

    def on_elected(self, msg: ElectedMessage,
                   signed: SignedMessage[ElectedMessage]) -> State:
        from .follower import Follower

        # Transition to follower state if election proof is valid and
        # for a future term
        if not msg.verify(self.config):
            return self
        if msg.term <= self.term:
            return self
        leader_commit_idx, commit_idx_a_cert = msg.leader_commit_idx()
        return Follower(msg.term, leader_commit_idx,
                        commit_idx_a_cert, self)

    def on_timeout(self, context: object) -> State:
        '''Returns resulting state.'''
        return self

    @property
    def config(self) -> ServerConfig:
        return self.server.config
