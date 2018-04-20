import asyncio
import typing
from collections import defaultdict

from ..config import ClientConfig
from ..messages import (ClientRequest, ClientRequestFailure, ClientResponse,
                        Message, SignedMessage)
from ..messengers.asyncio import AsyncIoMessenger
from ..messengers.listener import MessengerListener
from ..timeout_managers.asyncio import AsyncIoTimeoutManager
from ..timeout_managers.listener import TimeoutListener
from ..util.asyncio_shutdown import shutdown


class AsyncIoClient(MessengerListener, TimeoutListener):

    def __init__(self, config: ClientConfig,
                 client_addr: typing.Tuple[str, int],
                 server_addrs: typing.Dict[int, typing.Tuple[str, int]]) -> None:
        self.config = config
        self.client_addr = client_addr
        self.server_addrs = server_addrs
        self.loop = asyncio.get_event_loop()
        self.messenger = AsyncIoMessenger(config, {self.config.client_id: client_addr},
                                          server_addrs, config.client_id, True, self.loop)
        self.messenger.add_listener(self)
        self.timeout_manager = AsyncIoTimeoutManager(self.loop)
        self.timeout_manager.add_listener(self)
        self.seqno = 0

        # Request that we have sent and are currently waiting on responses for
        self.active_request = None  # type: bytes

        # Used to wait until we get f + 1 matching responses.
        self.responses_sem = None  # type: asyncio.Semaphore

        # map from response -> set of server ids
        self.responses = None  # type: typing.Dict[bytes, typing.Set[int]]

        # map from server id -> seqno
        self.failures = None  # type: typing.Dict[int, int]

        # Result of the request. On success, this is the byte string returned by
        # the application on the server. On failure, this is the sequence number
        # we should raise our sequence number to before retrying.
        self.result = None  # type: object

    def send_request(self, operation: bytes) -> bytes:
        assert isinstance(operation, bytes)
        result = self.loop.run_until_complete(
            self._send_request(operation))
        self.seqno += 1
        return result

    def on_message(self, msg: Message, signed: SignedMessage) -> None:
        if isinstance(msg, ClientResponse):
            self.on_response(msg)
        elif isinstance(msg, ClientRequestFailure):
            self.on_failure(msg)

    def on_response(self, msg: ClientResponse) -> None:
        print('a')
        if self.active_request is None:
            return
        print('b')
        if msg.seqno != self.seqno or msg.requester != self.config.client_id:
            return
        print('c')
        self._add_result(msg.sender_id, msg.result)

    def on_failure(self, msg: ClientRequestFailure) -> None:
        if self.active_request is None:
            return
        if msg.requester != self.config.client_id or msg.max_seqno < self.seqno:
            return

        # If max_seqno == our current seqno, the server has already executed the
        # request we are trying to get a response for, so we can use the response
        # included in the failure message
        if msg.max_seqno == self.seqno:
            self._add_result(msg.sender_id, msg.result)

        # Otherwise, max_seqno > our current seqno. If f + 1 servers indicate that
        # our local seqno is out of date, we increase it and retry the request
        else:
            assert msg.max_seqno >= self.seqno
            self.failures[msg.sender_id] = msg.max_seqno
            if len(self.failures) >= self.config.f + 1:
                new_seqno = min(self.failures.values()) + 1
                assert new_seqno > self.seqno
                self.seqno = new_seqno
                self._resend_request()

    def on_timeout(self, context: object) -> None:
        pass

    def start_server(self) -> None:
        self.messenger.start_server()

    def shutdown(self) -> None:
        self.loop.run_until_complete(shutdown(self.loop))
        self.loop.close()

    def _add_result(self, server_id: int, result: bytes) -> None:
        assert self.responses_sem is not None
        print(server_id)
        self.responses[result].add(server_id)

        # If we have f + 1 responses, increment the semaphore so we can stop
        # blocking in send_request and return the result
        if len(self.responses[result]) >= self.config.f + 1:
            self.result = result
            self.responses_sem.release()

    async def _send_request(self, operation: bytes) -> bytes:
        self.active_request = operation
        self.responses_sem = asyncio.Semaphore(value=0, loop=self.loop)
        self._resend_request()
        await self.responses_sem.acquire()
        if isinstance(self.result, bytes):  # successful
            return self.result
        elif isinstance(self.result, int):  # failure, must raise seqno and retry
            self.seqno = self.result
            return await self._send_request(operation)
        else:
            assert False

    def _resend_request(self):
        self.responses = defaultdict(set)
        self.failures = {}
        self.result = None
        req = ClientRequest(self.config.client_id, self.seqno,
                            self.active_request)
        self.messenger.broadcast_server_message(req)
