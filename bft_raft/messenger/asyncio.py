import asyncio
import typing
import struct
import pickle

from ..messages.base import Message, ServerMessage, SignedMessage
from .listener import MessengerListener
from .base import Messenger


class AsyncIoMessenger(Messenger):
    '''asyncio implementation of Messenger.'''

    def __init__(self, clients: typing.Dict[int, typing.Tuple[str, int, object]],
                 servers: typing.Dict[int, typing.Tuple[str, int, object]],
                 server_id: int, private_key,
                 loop: asyncio.AbstractEventLoop) -> None:
        self._clients = clients  # map from client id to (ip, port, public_key)
        self._servers = servers  # map from server id to (ip, port, public_key)
        self._server_id = server_id
        self._private_key = private_key
        self._loop = loop
        self._listeners = []  # type: list
        self._started_server = False  # Whether start_server has been called
        self._writers = {}  # type: ignore
        self._opening_queues = {}  # type: ignore

    def start_server(self) -> None:
        '''Start listening for incoming messages.'''
        assert not self._started_server
        my_addr = self._servers[self._server_id][0]
        my_port = self._servers[self._server_id][1]
        self._loop.create_task(
            asyncio.start_server(
                lambda r, w: self._loop.create_task(
                    self._handle_connection(r, w)),
                my_addr,
                my_port,
                loop=self._loop))

    def add_listener(self, listener: MessengerListener):
        self._listeners.append(listener)

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
            if i != self._server_id:
                self.send_server_message(i, message)

    async def _send_message(self, addr: str, port: int, message: Message) -> None:
        # Remove any closed StreamWriters from this node's writers list
        self._writers[(addr, port)] = [
            w for w in self._writers[(addr, port)] if not w.transport.is_closing()]
        msg = SignedMessage(message, self._private_key)

        # If there are any left in the writers list, send the message
        if self._writers[(addr, port)]:
            msg_raw = pickle.dumps(msg)
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
            self._opening_queues[(addr, port)] = [message]

            # Try to open the connection.
            try:
                writer = await asyncio.open_connection(addr, port)
                print('Opened connection with %s:%d' % (addr, port))

                # Send queued messages to the node if the connection was successful.
                for m in self._opening_queues[(addr, port)]:
                    m_raw = pickle.dumps(m)
                    writer.write(struct.pack('I', len(m_raw)))  # send message size
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
                msg = pickle.loads(msg_raw)
                if not isinstance(msg, SignedMessage):
                    raise RuntimeError

                # Verify signature
                from_client = msg.message.from_client
                if from_client:
                    pubkey = self._clients[msg.message.sender_id][2]
                else:
                    pubkey = self._servers[msg.message.sender_id][2]
                if not msg.verify(pubkey):
                    raise RuntimeError

                # dispatch to listeners
                for l in self._listeners:
                    l.on_message(msg)

            except (RuntimeError, KeyError, asyncio.IncompleteReadError):
                writer.close()
                break
