import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Crypto.PublicKey import RSA
from bft_raft.application import Application
from bft_raft.config import ServerConfig
from bft_raft.servers.asyncio import AsyncIoServer


class Echo(Application):
    def handle_request(self, operation: str, client_id: int) -> str:
        print('OPERATION: %s' % operation)
        return operation


client_addrs = {
    0: ('127.0.0.1', 8000),
    1: ('127.0.0.1', 8001),
    2: ('127.0.0.1', 8002),
    3: ('127.0.0.1', 8003),
    4: ('127.0.0.1', 8004)
}

server_addrs = {
    0: ('127.0.0.1', 9000),
    1: ('127.0.0.1', 9001),
    2: ('127.0.0.1', 9002),
    3: ('127.0.0.1', 9003),
    4: ('127.0.0.1', 9004)
}


def main():
    server_id = int(sys.argv[1])
    client_pubkeys = read_pubkeys('client', 5)
    server_pubkeys = read_pubkeys('server', 5)
    privkey = RSA.importKey(open('server%d_private.pem' % server_id, 'r').read())
    config = ServerConfig(server_id, client_pubkeys, server_pubkeys, privkey)
    app = Echo()
    server = AsyncIoServer(config, app, client_addrs, server_addrs)
    server.run()


def read_pubkeys(prefix, num_keys):
    public = {}
    for i in range(num_keys):
        public_fname = '%s%d_public.pem' % (prefix, i)
        public_f = open(public_fname, 'r')
        public[i] = RSA.importKey(public_f.read())
    return public


if __name__ == "__main__":
    main()
