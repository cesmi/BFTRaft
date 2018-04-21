from ..messages import Message


class MessengerListener(object):
    def on_message(self, msg: Message) -> None:
        '''Called when a message is received.'''
        raise NotImplementedError
