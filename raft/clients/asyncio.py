import asyncio
import typing

from ..config import ClientConfig
from ..messages import (ClientRequest, ClientRequestFailure,
                        ClientResponse, Message)
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

        # Used to wait until we get a response.
        self.response_sem = None  # type: asyncio.Semaphore

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

    def on_message(self, msg: Message) -> None:
        if isinstance(msg, ClientResponse):
            self.on_response(msg)
        elif isinstance(msg, ClientRequestFailure):
            self.on_failure(msg)

    def on_response(self, msg: ClientResponse) -> None:
        if self.active_request is None:
            return
        if msg.seqno != self.seqno or msg.requester != self.config.client_id:
            return
        self.result = msg.result
        self.response_sem.release()

    def on_failure(self, msg: ClientRequestFailure) -> None:
        if self.active_request is None:
            return
        if msg.requester != self.config.client_id or msg.max_seqno < self.seqno:
            return

        # If max_seqno == our current seqno, the server has already executed the
        # request we are trying to get a response for, so we can use the response
        # included in the failure message
        if msg.max_seqno == self.seqno:
            self.result = msg.result
            self.response_sem.release()

        # Otherwise, max_seqno > our current seqno. Increase local seqno and
        # retry the request
        else:
            assert msg.max_seqno >= self.seqno
            self.seqno = msg.max_seqno
            self._send_request_msg(timeout=False)

    def on_timeout(self, context: object) -> None:
        if isinstance(context, RequestTimeout):
            self.on_request_timeout(context)
        else:
            super(AsyncIoClient, self).on_timeout(context)

    def on_request_timeout(self, context: 'RequestTimeout') -> None:
        if self.active_request is not None and context.seqno == self.seqno:
            self.config.double_timeout()
            self._send_request_msg()

    def start_server(self) -> None:
        self.messenger.start_server()

    def shutdown(self) -> None:
        self.loop.run_until_complete(shutdown(self.loop))
        self.loop.close()

    async def _send_request(self, operation: bytes) -> bytes:
        self.active_request = operation
        self.response_sem = asyncio.Semaphore(value=0, loop=self.loop)
        self.result = None
        self._send_request_msg()
        await self.response_sem.acquire()
        assert isinstance(self.result, bytes)
        return self.result

    def _send_request_msg(self, timeout=True):
        req = ClientRequest(self.config.client_id, self.seqno,
                            self.active_request)
        self.messenger.broadcast_server_message(req)
        if timeout:
            self.timeout_manager.set_timeout(self.config.timeout,
                                             RequestTimeout(self.seqno))


class RequestTimeout(object):
    def __init__(self, seqno: int) -> None:
        self.seqno = seqno
