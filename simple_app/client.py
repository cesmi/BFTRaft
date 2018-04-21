import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from simple_app.config import client_addrs, client_pubkeys, server_addrs, \
    server_pubkeys, read_privkey
from bft_raft.config import ClientConfig
from bft_raft.clients.asyncio import AsyncIoClient

NUM_MESSAGES = 50


def main():
    client_id = int(sys.argv[1])
    privkey = read_privkey('client', client_id)
    config = ClientConfig(client_id, client_pubkeys, server_pubkeys, privkey)
    config.enable_logging = False
    client = AsyncIoClient(config, client_addrs[client_id], server_addrs)
    client.start_server()

    messages = ['client %d message %d' % (client_id, i)
                for i in range(NUM_MESSAGES)]
    for i, msg in enumerate(messages):
        if i % 25 == 0:
            print('%d/%d' % (i, len(messages)))
        resp = client.send_request(msg.encode()).decode()
        assert resp == msg
    client.shutdown()
    print('done')


if __name__ == "__main__":
    main()
