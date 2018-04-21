

class BaseClient(object):

    def send_request(self, operation: bytes) -> bytes:
        '''Sends a request to the servers to perform an operation and
        blocks until the request is safely replicated and executed. Returns
        the result of the operation.'''
        raise NotImplementedError
