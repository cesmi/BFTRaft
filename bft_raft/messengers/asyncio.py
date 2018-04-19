import asyncio
import pickle
import struct
import typing
from collections import defaultdict

from ..config import BaseConfig
from ..messages import Message, ServerMessage, SignedMessage
from .messenger import Messenger


class AsyncIoMessenger(Messenger):
    '''asyncio implementation of Messenger.'''

    def __init__(self,
                 config: BaseConfig,
                 clients: typing.Dict[int, typing.Tuple[str, int]],
                 servers: typing.Dict[int, typing.Tuple[str, int]],
                 node_id: int,
                 is_client: bool,
                 loop: asyncio.AbstractEventLoop) -> None:
        super(AsyncIoMessenger, self).__init__(config)
        self._clients = clients  # map from client id to (ip, port)
        self._servers = servers  # map from server id to (ip, port)
        self._node_id = node_id
        self._is_client = is_client
        self._loop = loop
        self._started_server = False  # Whether start_server has been called
        self._writers = defaultdict(list)  # type: ignore
        self._opening_queues = defaultdict(lambda: None)  # type: ignore

    def start_server(self) -> None:
        '''Start listening for incoming messages.'''
        assert not self._started_server
        self._started_server = True
        if self._is_client:
            my_addr = self._clients[self._node_id][0]
            my_port = self._clients[self._node_id][1]
        else:
            my_addr = self._servers[self._node_id][0]
            my_port = self._servers[self._node_id][1]
        self._loop.create_task(
            asyncio.start_server(
                lambda r, w: self._loop.create_task(
                    self._handle_connection(r, w)),
                my_addr,
                my_port,
                loop=self._loop))

    def send_server_message(self, server_id: int, message: ServerMessage) -> None:
        addr = self._servers[server_id][0]
        port = self._servers[server_id][1]
        self._loop.create_task(self._send_message(addr, port, message))

    def send_client_message(self, client_id: int, message: Message) -> None:
        addr = self._clients[client_id][0]
        port = self._servers[client_id][1]
        self._loop.create_task(self._send_message(addr, port, message))

    def broadcast_server_message(self, message) -> None:
        for i in range(0, len(self._servers)):
            if not self._is_client and i == self._node_id:
                continue
            self.send_server_message(i, message)

    async def _send_message(self, addr: str, port: int, message: Message) -> None:
        # Remove any closed StreamWriters from this node's writers list
        self._writers[(addr, port)] = [
            w for w in self._writers[(addr, port)] if not w.transport.is_closing()]
        signed = SignedMessage(message, self.config.private_key)

        # If there are any left in the writers list, send the message
        if self._writers[(addr, port)]:
            msg_raw = pickle.dumps(signed)
            writer = self._writers[(addr, port)][0]
            writer.write(struct.pack('I', len(msg_raw)))  # send message size
            writer.write(msg_raw)
            return

        # Otherwise, we wait until we open a new connection to send the message.
        # If we are currently trying to open a connection, add the message to the
        # appropriate opening queue.
        if self._opening_queues[(addr, port)] is not None:
            self._opening_queues[(addr, port)].append(message)

        # If we are not currently trying to open the connection, we try to open
        # the connection ourself.
        else:
            # Create the opening queue and add the message to it.
            self._opening_queues[(addr, port)] = [signed]

            # Try to open the connection.
            try:
                _, writer = await asyncio.open_connection(addr, port)
                print('Opened connection with %s:%d' % (addr, port))

                # Send queued messages to the node if the connection was successful.
                for m in self._opening_queues[(addr, port)]:
                    m_raw = pickle.dumps(m)
                    # send message size
                    writer.write(struct.pack('I', len(m_raw)))
                    writer.write(m_raw)

            except ConnectionError:
                print('Failed to open connection with %s:%d' % (addr, port))

            # Erase the opening queue
            self._opening_queues[(addr, port)] = None

    async def _handle_connection(self, reader: asyncio.StreamReader,
                                 writer: asyncio.StreamWriter) -> None:
        # Recv message and pass to callback
        while True:
            try:
                msg_size_raw = await reader.readexactly(struct.calcsize('I'))
                msg_size = struct.unpack('I', msg_size_raw)[0]
                msg_raw = await reader.readexactly(msg_size)
                signed = pickle.loads(msg_raw)
            except asyncio.IncompleteReadError:
                break
            if not isinstance(signed, SignedMessage):
                break

            # Verify signature / message validity and invoke callback
            if not self.verify_and_deliver(signed):
                break
        writer.close()
