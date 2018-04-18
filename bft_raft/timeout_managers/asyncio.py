import asyncio
from .timeout_manager import TimeoutManager
from .listener import TimeoutListener


class AsyncIoTimeoutManager(TimeoutManager):
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._listeners = []  # type: list

    def add_listener(self, listener: TimeoutListener):
        self._listeners.append(listener)

    def set_timeout(self, time: float, context: object):
        self._loop.create_task(AsyncIoTimeoutManager._timeout(
            self, time, context))

    async def _timeout(self, time: float, context: object):
        '''Coroutine that calls on_timeout after a given amount of time.'''
        await asyncio.sleep(time)
        for l in self._listeners:
            l.on_timeout(context)
