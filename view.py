from queue import Queue
from asyncio import get_running_loop


class View:
    def __init__(self, func, take_request=False):
        self.func = func
        self.take_request = take_request
        self.await_send = False
        self.request = None

    def set_request(self, request):
        self.request = request

    def set_await_send(self, await_send):
        self.await_send = await_send

    def __call__(self) -> Queue:
        args = ()
        result = Queue()
        loop = get_running_loop()

        async def send(resp):
            async def inner(): return resp
            result.put(loop.create_task(inner()))
            return resp

        if self.take_request: args = (self.request,) + args
        if self.await_send: args = (send,) + args

        result.put(loop.create_task(self.func(*args)))
        return result
