from ..messages import (AppendEntriesRequest, AppendEntriesSuccess,
                        CommitMessage, ElectedMessage, SignedMessage,
                        VoteMessage)
from ..servers.base import BaseServer
from .state import State

from .voter import Voter

class ByzantineVoter0(Voter):
    def __init__(self, term: int,
                 server: BaseServer,
                 copy_from: State) -> None:
        print('ByzantineVoter0')
        super(ByzantineVoter0, self).__init__(term, server, copy_from)

    def send_vote(self):
        super(ByzantineVoter0, self).send_vote()

    def start(self):
        super(ByzantineVoter0, self).start()

    def on_append_entries_request(self, msg: AppendEntriesRequest,
                                  signed: SignedMessage[AppendEntriesRequest]) -> 'State':
        super(ByzantineVoter0, self).on_append_entries_request(msg, signed)
        return self

    def on_append_entries_success(self, msg: AppendEntriesSuccess,
                                  signed: SignedMessage[AppendEntriesSuccess]) -> 'State':
        super(ByzantineVoter0, self).on_append_entries_success(msg, signed)
        return self

    def on_commit(self, msg: CommitMessage,
                  signed: SignedMessage[CommitMessage]) -> 'State':
        super(ByzantineVoter0, self).on_commit(msg, signed)
        return self

    def on_elected(self, msg: ElectedMessage,
                   signed: SignedMessage[ElectedMessage]) -> 'State':
        print('Elected')
        from .byzantine_follower import ByzantineFollower0

        leader_commit_idx, commit_idx_a_cert = msg.leader_commit_idx()
        return ByzantineFollower0(msg.term, leader_commit_idx,
                        commit_idx_a_cert, self)
