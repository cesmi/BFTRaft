from ..messages.base import SignedMessage


class MessengerListener(object):
    def on_message(self, message: SignedMessage) -> None:
        '''Called when a message is received.
        The signature is verified before this function is called.'''
        raise NotImplementedError
