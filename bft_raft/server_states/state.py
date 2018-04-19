from collections import defaultdict
from typing import Dict, List, Tuple, TypeVar  # pylint:disable=W0611

from ..config import ServerConfig
from ..messages import (ACert, AppendEntriesRequest,  # pylint:disable=W0611
                        AppendEntriesSuccess, CatchupRequest, CatchupResponse,
                        CCert, ClientRequest, CommitMessage, ElectedMessage,
                        ElectionProofRequest, LogEntry, Message, SignedMessage,
                        VoteMessage, VoteRequest)

if False:  # pylint:disable=W0125
    # (just for type checking; if statement avoids circular import)
    from ..servers.base import BaseServer  # pylint:disable=W0611


class State(object):
    def __init__(self, server: 'BaseServer', copy_from: 'State' = None,
                 term: int = None) -> None:
        self.server = server  # type: BaseServer
        self.log = []  # type: List[LogEntry]
        self.term = 0
        self.latest_a_cert = None  # type: ACert
        self.applied_c_cert = None  # type: CCert

        # Map from client id to (seqno, result) pair for the request with
        # greatest sequence number executed by a client.
        self.latest_req_per_client = {}  # type: Dict[int, Tuple[int, bytes]]

        # Votes received by this server.
        # Map from term id to server id to signed vote message.
        self.votes = defaultdict()  # type: Dict[int, Dict[int, SignedMessage[VoteMessage]]]

        if copy_from is not None:
            self.log = copy_from.log
            self.term = copy_from.term
            self.applied_c_cert = copy_from.applied_c_cert
            self.votes = copy_from.votes

        if term is not None:
            assert term >= self.term
            self.term = term

            # Discard votes from before the new term
            for t in self.votes.keys():
                if t <= self.term:
                    del self.votes[t]

    def start(self):
        '''Performs any actions a server in this state should perform on startup.'''
        raise NotImplementedError

    def on_message(self, msg: Message, signed: SignedMessage) -> 'State':
        '''Invokes the appropriate callback for msg. Returns resulting state.'''
        if isinstance(msg, AppendEntriesRequest):
            return self.on_append_entries_request(msg, signed)
        elif isinstance(msg, AppendEntriesSuccess):
            return self.on_append_entries_success(msg, signed)
        elif isinstance(msg, ClientRequest):
            return self.on_client_request(msg, signed)
        elif isinstance(msg, CommitMessage):
            return self.on_commit(msg, signed)
        elif isinstance(msg, VoteMessage):
            return self.on_vote(msg, signed)
        elif isinstance(msg, VoteRequest):
            return self.on_vote_request(msg, signed)
        elif isinstance(msg, ElectedMessage):
            return self.on_elected(msg, signed)
        elif isinstance(msg, ElectionProofRequest):
            return self.on_election_proof_request(msg, signed)
        elif isinstance(msg, CatchupRequest):
            return self.on_catchup_request(msg, signed)
        elif isinstance(msg, CatchupResponse):
            return self.on_catchup_response(msg, signed)
        else:
            assert False, 'unhandled message type %s' % msg.__class__.__name__

    def on_append_entries_request(self, msg: AppendEntriesRequest,
                                  signed: SignedMessage[AppendEntriesRequest]) -> 'State':
        # request proof of election if sender claims higher term
        if msg.term > self.term:
            self._request_election_proof(msg.term)
        return self

    def on_append_entries_success(self, msg: AppendEntriesSuccess,
                                  signed: SignedMessage[AppendEntriesSuccess]) -> 'State':
        # request proof of election if sender claims higher term
        if msg.term > self.term:
            self._request_election_proof(msg.term)
        return self

    def on_client_request(self, msg: ClientRequest,
                          signed: SignedMessage[ClientRequest]) -> 'State':
        return self

    def on_commit(self, msg: CommitMessage,
                  signed: SignedMessage[CommitMessage]) -> 'State':
        # request proof of election if sender claims higher term
        if msg.term > self.term:
            self._request_election_proof(msg.term)
        return self

    def on_vote(self, msg: VoteMessage,
                signed: SignedMessage[VoteMessage]) -> 'State':
        from .candidate import Candidate

        # Add vote to votes map if term > current term
        if msg.term <= self.term:
            return self
        self.votes[msg.term][msg.sender_id] = signed

        # If have >= f votes, one must be from a correct replica,
        # so we can transition to Candidate state and send a vote
        # request to all other replicas
        if len(self.votes[msg.term]) >= self.config.f:
            assert self.config.server_id not in self.votes[msg.term]
            new_state = Candidate(msg.term, self.votes[msg.term], self.server, self)
            new_state.send_vote_request()
            return new_state
        return self

    def on_vote_request(self, msg: VoteRequest,
                        signed: SignedMessage[VoteRequest]) -> 'State':
        from .voter import Voter

        # Send a vote if request is for a future term.
        if msg.term <= self.term:
            return self
        new_state = Voter(msg.term, self.server, self)
        new_state.send_vote()
        return new_state

    def on_elected(self, msg: ElectedMessage,
                   signed: SignedMessage[ElectedMessage]) -> 'State':
        from .follower import Follower

        # Transition to follower state if election proof is for a future term.
        if msg.term <= self.term:
            return self
        leader_commit_idx, commit_idx_a_cert = msg.leader_commit_idx()
        return Follower(msg.term, leader_commit_idx,
                        commit_idx_a_cert, self)

    def on_election_proof_request(self, msg: ElectionProofRequest,
                                  signed: SignedMessage[ElectionProofRequest]) -> 'State':
        return self

    def on_catchup_request(self, msg: CatchupRequest,
                           signed: SignedMessage[CatchupRequest]) -> 'State':
        if msg.last_slot < len(self.log):
            entries = self.log[msg.first_slot:msg.last_slot]
            resp = CatchupResponse(self.config.server_id, self.term,
                                   msg.first_slot, entries)
            self.server.messenger.broadcast_server_message(resp)
        return self

    def on_catchup_response(self, msg: CatchupResponse,
                            signed: SignedMessage[CatchupResponse]) -> 'State':
        return self

    def on_timeout(self, context: object) -> 'State':
        '''Returns resulting state.'''
        return self

    def _request_election_proof(self, term) -> None:
        primary = term % self.config.num_servers
        leader_proof_req = ElectionProofRequest(
            self.config.server_id, term)
        self.server.messenger.send_server_message(primary, leader_proof_req)

    @property
    def config(self) -> ServerConfig:
        return self.server.config
