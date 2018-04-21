import traceback
from typing import List  # pylint:disable=W0611

from ..config import BaseConfig
from ..messages import Message, ServerMessage
from .listener import MessengerListener


class Messenger(object):
    '''Manages sending and receiving messages to/from clients and other replicas.

    When a message is received, the validity of its signature is checked
    and then on_message is called on all attached listeners.'''

    def __init__(self, config: BaseConfig) -> None:
        self.listeners = []  # type: List[MessengerListener]
        self.config = config

    def add_listener(self, listener: MessengerListener):
        '''Add a new MessengerListener to the list of subscribers.'''
        self.listeners.append(listener)

    def send_server_message(self, server_id: int, message: ServerMessage) -> None:
        '''Sends a message to a server.'''
        raise NotImplementedError

    def send_client_message(self, client_id: int, message: Message) -> None:
        '''Sends a message to a client.'''
        raise NotImplementedError

    def broadcast_server_message(self, message) -> None:
        '''Sends a message to all other servers.'''
        raise NotImplementedError

    def deliver(self, msg: Message) -> bool:
        '''Invokes on_message on all attached listeners.
        Returns true on success, false, on failure.'''
        self.config.log('Received %s from %d' % (msg.__class__.__name__, msg.sender_id))

        # dispatch to listeners
        for l in self.listeners:
            try:
                l.on_message(msg)
            except Exception as e:  # pylint:disable=W0703
                if isinstance(e, KeyboardInterrupt):
                    raise e
                self.config.log('on_message callback raised exception', force=True)
                self.config.log(traceback.format_exc(), force=True)
                return False
        return True
