from .listener import TimeoutListener


class TimeoutManager(object):
    '''Manages setting timeouts and calling callbacks when they expire.'''

    def add_listener(self, listener: TimeoutListener):
        '''Adds a listener that on_timeout should be called on when timeouts expire.'''
        raise NotImplementedError

    def set_timeout(self, time: float, context: object):
        '''Calls on_timeout after a given amount of time.'''
        raise NotImplementedError
