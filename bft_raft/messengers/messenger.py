from ..messages import Message, ServerMessage
from .listener import MessengerListener


class Messenger(object):
    '''Manages sending and receiving messages to/from clients and other replicas.

    When a message is received, the validity of its signature is checked
    and then on_message is called on all attached listeners.'''

    def add_listener(self, listener: MessengerListener):
        '''Add a new MessengerListener to the list of subscribers.'''
        raise NotImplementedError

    def send_server_message(self, server_id: int, message: ServerMessage) -> None:
        '''Signs a message and sends it to another server.'''
        raise NotImplementedError

    def send_client_message(self, client_id: int, message: Message) -> None:
        '''Signs a message and sends it to a client.'''
        raise NotImplementedError

    def broadcast_server_message(self, message) -> None:
        '''Signs a message and sends it to all other servers.'''
        raise NotImplementedError
