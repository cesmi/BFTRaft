import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from simple_app_raft.config import client_addrs, server_addrs
from raft.application import Application
from raft.config import ServerConfig
from raft.servers.asyncio import AsyncIoServer


class LogAndEcho(Application):
    def __init__(self, logfile):
        self.logfile = logfile

    def handle_request(self, operation: bytes, client_id: int) -> bytes:
        print('OPERATION: %s' % operation.decode())
        self.logfile.write(operation.decode() + '\n')
        self.logfile.flush()
        return operation


def main():
    server_id = int(sys.argv[1])
    config = ServerConfig(server_id, len(server_addrs))
    config.enable_logging = True
    app = LogAndEcho(open('server%d_log.txt' % server_id, 'w'))
    server = AsyncIoServer(config, app, client_addrs, server_addrs)
    server.run()


if __name__ == "__main__":
    main()
