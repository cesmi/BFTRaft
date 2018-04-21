import typing
from ..application import Application
from ..config import ServerConfig
from ..messengers.memory_queue import MemoryQueueMessenger, SentMessage
from ..timeout_managers.memory_queue import MemoryQueueTimeoutManager
from .base import BaseServer


class MemoryQueueServer(BaseServer):
    '''Server that uses MemoryQueueMessenger and MemoryQueueTimeoutManager.

    Sent messages and set timeouts are stored in queues rather than actually being
    sent over the network or setting timers for the timeouts. The queues can be
    accessed with get_sent_message and get_timeout.'''

    def __init__(self, config: ServerConfig, application: Application) -> None:
        messenger = MemoryQueueMessenger(config)
        timeout_manager = MemoryQueueTimeoutManager()
        super(MemoryQueueServer, self).__init__(config, application,
                                                messenger, timeout_manager)
        self.memqueue_messenger = messenger
        self.memqueue_to_manager = timeout_manager

    def get_sent_message(self) -> SentMessage:
        '''Pops a sent message off the front of the queue and returns it.'''
        return self.memqueue_messenger.get_message()

    def get_timeout(self) -> typing.Tuple[float, object]:
        '''Pops a set timeout off the front of the queue and returns it.'''
        return self.memqueue_to_manager.get_timeout()
