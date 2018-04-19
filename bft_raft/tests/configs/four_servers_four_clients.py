from ...config import ServerConfig
from ..helpers.gen_keys import gen_keys

NUM_CLIENTS = 4
NUM_SERVERS = 4


client_public_keys, client_private_keys = gen_keys(range(NUM_CLIENTS))
server_public_keys, server_private_keys = gen_keys(range(NUM_SERVERS))


def build_server_config(server_id: int):
    return ServerConfig(
        server_id,
        client_public_keys,
        server_public_keys,
        server_private_keys[server_id])


server_configs = [build_server_config(i) for i in range(0, NUM_SERVERS)]
