class Application(object):
    '''Applications using BFTRaft implement operations here.'''

    def handle_request(self, operation: bytes, client_id: int) -> bytes:
        '''Handles an operation requested by a client, which is given as
        bytes, and returns the result to send back to the client as bytes.'''
        raise NotImplementedError
