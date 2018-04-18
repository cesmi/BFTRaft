from ..messages.base import SignedMessage


class AbstractState(object):
    def start(self) -> None:
        '''Performs any actions a server in this state should perform on startup.'''
        raise NotImplementedError

    def on_message(self, msg: SignedMessage):
        '''Returns resulting state.'''
        raise NotImplementedError

    def on_timeout(self, context: object):
        '''Returns resulting state.'''
        raise NotImplementedError
