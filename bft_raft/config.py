

class ServerConfig(object):
    '''Configuration settings for BFTRaft servers.'''

    def __init__(self,
                 server_id: int,
                 client_public_keys: dict,
                 server_public_keys: dict,
                 private_key) -> None:
        self.server_id = server_id
        self.client_public_keys = client_public_keys
        self.server_public_keys = server_public_keys
        self.private_key = private_key

    @property
    def num_servers(self):
        return len(self.server_public_keys)

    @property
    def f(self):
        '''Number of tolerated faults.'''
        return (self.num_servers - 1) / 3

    @property
    def quorum_size(self):
        return (2 * self.f) + 1


class ClientConfig(object):
    '''Configuration settings for BFTRaft clients.'''
