import asyncio
from asyncio.tasks import Task


async def shutdown(loop: asyncio.AbstractEventLoop):
    '''Coroutine to cancel all running tasks in an event loop.
    Source: https://gist.github.com/nvgoldin/30cea3c04ee0796ebd0489aa62bcf00a'''
    tasks = [task for task in Task.all_tasks() if task is not Task.current_task()]
    list(map(lambda task: task.cancel(), tasks))
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
