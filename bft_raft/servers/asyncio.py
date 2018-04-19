import asyncio
from ..application import Application
from ..config import ServerConfig
from ..messengers.asyncio import AsyncIoMessenger
from ..timeout_managers.asyncio import AsyncIoTimeoutManager
from .base import BaseServer


class AsyncIoServer(BaseServer):
    '''Server that uses AsyncIoMessenger and AsyncIoTimeoutManager.'''

    def __init__(self, config: ServerConfig, application: Application,
                 client_addrs: dict, server_addrs: dict) -> None:
        loop = asyncio.get_event_loop()
        messenger = AsyncIoMessenger(config, client_addrs, server_addrs,
                                     config.server_id, False, loop)
        timeout_manager = AsyncIoTimeoutManager(loop)
        super(AsyncIoServer, self).__init__(config, application,
                                            messenger, timeout_manager)
        self.loop = loop
        self.asyncio_messenger = messenger

    def run(self):
        self.messenger.start_server()
        self.loop.run_forever()
