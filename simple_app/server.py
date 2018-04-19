import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from simple_app.config import client_addrs, client_pubkeys, server_addrs, \
    server_pubkeys, read_privkey
from bft_raft.application import Application
from bft_raft.config import ServerConfig
from bft_raft.servers.asyncio import AsyncIoServer


class PrintAndEcho(Application):
    def handle_request(self, operation: bytes, client_id: int) -> bytes:
        print('OPERATION: %s' % str(operation))
        return operation


def main():
    server_id = int(sys.argv[1])
    privkey = read_privkey('server', server_id)
    config = ServerConfig(server_id, client_pubkeys, server_pubkeys, privkey)
    app = PrintAndEcho()
    server = AsyncIoServer(config, app, client_addrs, server_addrs)
    server.run()


if __name__ == "__main__":
    main()
