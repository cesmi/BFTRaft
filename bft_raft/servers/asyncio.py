import asyncio
from ..application import Application
from ..config import ServerConfig
from ..messengers import AsyncIoMessenger
from ..timeout_managers import AsyncIoTimeoutManager
from .base import BaseServer


class AsyncIoServer(BaseServer):
    '''Server that uses AsyncIoMessenger and AsyncIoTimeoutManager.'''

    def __init__(self, config: ServerConfig, application: Application,
                 client_addrs: dict, server_addrs: dict) -> None:
        loop = asyncio.get_event_loop()
        clients = {}
        servers = {}
        for client_id, pubkey in config.client_public_keys.items():
            addr = client_addrs[client_id]
            clients[client_id] = (client_addrs[0], client_addrs[1], pubkey)
        for server_id, pubkey in config.server_public_keys.items():
            addr = server_addrs[server_id]
            servers[server_id] = (server_addrs[0], server_addrs[1], pubkey)
        messenger = AsyncIoMessenger(clients, servers, config.server_id,
                                     config.private_key, loop)
        timeout_manager = AsyncIoTimeoutManager(loop)
        super(AsyncIoServer, self).__init__(config, application,
                                            messenger, timeout_manager)
        self.loop = loop
        self.asyncio_messenger = messenger

    def run(self):
        self.messenger.start_server()
        self.loop.run_forever()
