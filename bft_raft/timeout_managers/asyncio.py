import asyncio
from .timeout_manager import TimeoutManager


class AsyncIoTimeoutManager(TimeoutManager):
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        super(AsyncIoTimeoutManager, self).__init__()
        self._loop = loop

    def set_timeout(self, time: float, context: object):
        self._loop.create_task(AsyncIoTimeoutManager._timeout(
            self, time, context))

    async def _timeout(self, time: float, context: object):
        '''Coroutine that calls on_timeout after a given amount of time.'''
        await asyncio.sleep(time)
        self.dispatch(context)
