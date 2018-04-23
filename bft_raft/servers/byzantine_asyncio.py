from .asyncio import AsyncIoServer, ServerConfig, Application, asyncio, \
    AsyncIoMessenger, AsyncIoTimeoutManager

from .byzantine_base import ByzantineBaseServer


class ByzantineAsyncIoServer(ByzantineBaseServer):
    '''Byzantine version of AsyncIoServer'''

    def __init__(self, config: ServerConfig, application: Application,
                 client_addrs: dict, server_addrs: dict, byzantine_type: int) -> None:

        loop = asyncio.get_event_loop()
        messenger = AsyncIoMessenger(config, client_addrs, server_addrs,
                                     config.server_id, False, loop)
        timeout_manager = AsyncIoTimeoutManager(loop)
        ByzantineBaseServer.__init__(self, config, application, messenger,
                                     timeout_manager, byzantine_type)
        self.loop = loop
        self.asyncio_messenger = messenger

    def run(self):
        AsyncIoServer.run(self)
