

class BaseConfig(object):
    def __init__(self,
                 client_public_keys: dict,
                 server_public_keys: dict,
                 private_key) -> None:
        self.client_public_keys = client_public_keys
        self.server_public_keys = server_public_keys
        self.private_key = private_key
        assert ((self.num_clients - 1) % 3) == 0

    @property
    def num_servers(self):
        return len(self.server_public_keys)

    @property
    def num_clients(self):
        return len(self.client_public_keys)

    @property
    def f(self):
        '''Number of tolerated faults.'''
        return (self.num_servers - 1) / 3

    @property
    def quorum_size(self):
        return (2 * self.f) + 1


class ServerConfig(BaseConfig):
    '''Configuration settings for BFTRaft servers.'''

    def __init__(self,
                 server_id: int,
                 client_public_keys: dict,
                 server_public_keys: dict,
                 private_key) -> None:
        super(ServerConfig, self).__init__(
            client_public_keys, server_public_keys, private_key)
        self.server_id = server_id


class ClientConfig(BaseConfig):
    '''Configuration settings for BFTRaft clients.'''
