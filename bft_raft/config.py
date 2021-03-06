

class BaseConfig(object):
    def __init__(self,
                 client_public_keys: dict,
                 server_public_keys: dict,
                 private_key) -> None:
        self.client_public_keys = client_public_keys
        self.server_public_keys = server_public_keys
        self.private_key = private_key
        assert ((self.num_clients - 1) % 3) == 0

        self._timeout = 3  # type: float
        self.enable_logging = True

    def double_timeout(self) -> None:
        self._timeout *= 2

    def log(self, msg, force=False) -> None:
        if self.enable_logging or force:
            print(msg)

    @property
    def timeout(self) -> float:
        return self._timeout

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

    def __init__(self,
                 client_id: int,
                 server_public_keys: dict,
                 public_key,
                 private_key) -> None:
        super(ClientConfig, self).__init__(
            {client_id: public_key}, server_public_keys, private_key)
        self.client_id = client_id
