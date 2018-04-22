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
        super(ByzantineVoter0, self).__init__(term, self, copy_from)

    def send_vote(self):
        pass

    def start(self):
        pass

    def on_append_entries_request(self, msg: AppendEntriesRequest,
                                  signed: SignedMessage[AppendEntriesRequest]) -> 'State':
        pass

    def on_append_entries_success(self, msg: AppendEntriesSuccess,
                                  signed: SignedMessage[AppendEntriesSuccess]) -> 'State':
        pass

    def on_commit(self, msg: CommitMessage,
                  signed: SignedMessage[CommitMessage]) -> 'State':
        pass

    def on_elected(self, msg: ElectedMessage,
                   signed: SignedMessage[ElectedMessage]) -> 'State':
        pass
