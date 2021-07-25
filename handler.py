from .setting import Setting
from .asgi import AsgiApplication
from .path import Node, DNENode
from queue import Queue
from asyncio import get_running_loop


class Handler:
    def __init__(self, setting: Setting=None):
        self.setting = setting or Setting()
        self.application = AsgiApplication(self)
        self.pages = Node("", {})
        self.error_pages = {}

    def page(self, url="", method="GET", take_request=False):
        def inner(func):
            if isinstance(node := self.get_page(url), DNENode):
                urls = url.split("/")
                node = self.pages
                for u in urls:
                    next_node = node.get_node(u)
                    if isinstance(next_node, DNENode):
                        node.add_child(Node(u, {}))
                        node = node.get_node(u)
                inner(func)
            else:
                node.add_view(method.upper(), View(func, take_request))

            return func
        return inner

    def error_page(self, err_code=404, take_request=False):
        def inner(func):
            self.error_pages[err_code] = View(func, take_request)
        return inner

    def ingest_handler(self, handler, url):
        handler.pages.url = url
        self.pages.add_child(handler.pages)

    def get_page(self, url):
        return self.pages.get_node(url)


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

    def __call__(self, *args, **kwargs):
        result = Queue()
        loop = get_running_loop()

        async def send(resp):
            async def inner(): return resp
            result.put(loop.create_task(inner()))
            return resp

        if self.take_request: args = (self.request,) + args
        if self.await_send: args = (send,) + args

        result.put(loop.create_task(self.func(*args, **kwargs)))
        return result
