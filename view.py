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
        kwargs = {}
        result = Queue()
        loop = get_running_loop()

        async def send(resp):
            async def inner(): return resp
            result.put(loop.create_task(inner()))
            return resp

        if self.take_request: kwargs |= {"request": self.request}
        if self.await_send: kwargs |= {"send": send}

        result.put(loop.create_task(self.func(**kwargs)))
        return result
