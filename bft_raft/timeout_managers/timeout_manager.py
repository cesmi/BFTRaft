from .listener import TimeoutListener


class TimeoutManager(object):
    '''Manages setting timeouts and calling callbacks when they expire.'''

    def __init__(self):
        self.listeners = []  # type: ignore

    def add_listener(self, listener: TimeoutListener):
        '''Adds a listener that on_timeout should be called on when timeouts expire.'''
        self.listeners.append(listener)

    def set_timeout(self, time: float, context: object):
        '''Calls on_timeout after a given amount of time.'''
        raise NotImplementedError

    def dispatch(self, context: object):
        '''Invokes on_timeout on all attached listeners.'''
        for l in self.listeners:
            l.on_timeout(context)
