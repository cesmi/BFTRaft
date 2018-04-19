from operator import itemgetter
from .timeout_manager import TimeoutManager


class MemoryQueueTimeoutManager(TimeoutManager):
    '''Stores set timeouts in a priority queue instead of actually setting timeouts.
    Used for testing.'''

    def __init__(self) -> None:
        super(MemoryQueueTimeoutManager, self).__init__()
        self._timeouts = []  # type: ignore

    def get_timeout(self):
        '''Pops timeout off the front of the queue and returns it.'''
        if not self._timeouts:
            return None
        rval = self._timeouts[0]
        self._timeouts = self._timeouts[1:]
        return rval

    def set_timeout(self, time: float, context: object):
        self._timeouts = sorted(self._timeouts + [(time, context)],
                                key=itemgetter(0))
