import unittest

from .configs.four_servers_four_clients import (NUM_CLIENTS, NUM_SERVERS,
                                                server_configs)
from .helpers.echo_app import EchoApp
from ..messages import VoteMessage, VoteRequest
from ..servers.memory_queue import MemoryQueueServer, SentMessage
from ..server_states.candidate import Candidate
from ..server_states.voter import Voter


class TestElection(unittest.TestCase):

    def test_startup(self):
        servers = [MemoryQueueServer(c, EchoApp()) for c in server_configs]

        # check initial state
        self.assertIsInstance(servers[0].state, Candidate)
        for i in range(1, NUM_SERVERS):
            self.assertIsInstance(servers[i].state, Voter)

        # voters should send votes
        votes = []
        for i in range(1, NUM_SERVERS):
            msg = servers[i].get_sent_message()
            self.assertIsNotNone(msg)
            self.assertIsInstance(msg.message, VoteMessage)
            self.assertEqual(msg.send_type, SentMessage.Type.TO_SERVER)
            self.assertEqual(msg.recipient, 0)
            self.assertIsNone(msg.message.a_cert)
            votes.append(msg)

        # leader should not have sent anything
        self.assertIsNone(servers[0].get_sent_message())

        # after delivering f votes (i.e. 1) to the primary they should
        # become a candidate and send a VoteRequest to all other servers
        vote = votes.pop()
        servers[0].on_message(vote.message, vote.signed)
        vote_req = servers[0].get_sent_message()
        self.assertIsNotNone(vote_req)
        self.assertIsInstance(vote_req.message, VoteRequest)

        # upon receiving a vote request, the voters should send another vote
        # TODO

        # after delivering 2f votes (i.e. 2) to the primary they should
        # become a leader and send out an election proof
        # (no catchup is necessary here)
        # TODO
