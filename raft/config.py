

class BaseConfig(object):
    def __init__(self,
                 num_servers: int) -> None:
        self.num_servers = num_servers
        assert ((self.num_servers - 1) % 2) == 0

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
    def f(self):
        '''Number of tolerated faults.'''
        return (self.num_servers - 1) / 2

    @property
    def quorum_size(self):
        return self.f + 1


class ServerConfig(BaseConfig):
    '''Configuration settings for BFTRaft servers.'''

    def __init__(self,
                 server_id: int,
                 num_servers: int) -> None:
        super(ServerConfig, self).__init__(num_servers)
        self.server_id = server_id


class ClientConfig(BaseConfig):
    '''Configuration settings for BFTRaft clients.'''

    def __init__(self,
                 client_id: int,
                 num_servers: int) -> None:
        super(ClientConfig, self).__init__(num_servers)
        self.client_id = client_id
