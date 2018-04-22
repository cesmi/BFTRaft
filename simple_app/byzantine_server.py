import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from simple_app.server import read_privkey, ServerConfig, client_pubkeys, \
        server_pubkeys, LogAndEcho, AsyncIoServer, client_addrs, server_addrs

from bft_raft.servers.byzantine_asyncio import ByzantineAsyncIoServer

def main():
    print('Byzantine Server Startup!')
    server_id = int(sys.argv[1])
    byzantine_type = int(sys.argv[2])
    privkey = read_privkey('server', server_id)
    config = ServerConfig(server_id, client_pubkeys, server_pubkeys, privkey)
    config.enable_logging = True
    app = LogAndEcho(open('server%d_log.txt' % server_id, 'w'))
    server = ByzantineAsyncIoServer(config, app, client_addrs, server_addrs, byzantine_type)
    server.run()

if __name__ == "__main__":
    main()
