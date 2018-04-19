from ..messages import Message, SignedMessage


class MessengerListener(object):
    def on_message(self, msg: Message, signed: SignedMessage) -> None:
        '''Called when a message is received.
        The signature is verified before this function is called.'''
        raise NotImplementedError
