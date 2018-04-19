from ..messages import VoteMessage
from ..servers import BaseServer
from .state import State


class Voter(State):
    def __init__(self, term: int,
                 server: BaseServer,
                 copy_from: State) -> None:
        super(Voter, self).__init__(server, copy_from, term)

    def send_vote(self):
        vote = VoteMessage(self.config.server_id,
                           self.term, self.latest_a_cert)
        self.server.messenger.send_server_message(
            self.term % self.config.num_servers, vote)
        # TODO: set a timeout here

    def start(self):
        '''A server initially in the Voter state sends a vote to the primary.'''
        self.send_vote()
