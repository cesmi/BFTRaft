class Application(object):
    '''Applications using BFTRaft implement operations here.'''

    def handle_request(self, operation: str, client_id: int) -> str:
        '''Handles an operation requested by a client, which is given as a
        string, and returns the result to send back to the client as a string.'''
        raise NotImplementedError
