
class TimeoutListener(object):
    def on_timeout(self, context: object) -> None:
        '''Called when a timeout expires.'''
        raise NotImplementedError
