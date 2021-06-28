from .setting import Setting
from .asgi import AsgiApplication
from .wsgi import WsgiApplication
from .path import Node, DNENode


class Handler:
    def __init__(self, setting: Setting=None, be_async=True):
        self.setting = setting or Setting()
        self.application = AsgiApplication(self) if be_async else WsgiApplication(self)
        self.pages = Node("", {})

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
        return inner

    def get_page(self, url):
        return self.pages.get_node(url)

    def get_page_func(self, url, method="GET"):
        return self.get_page(url).views[method.upper()]


class View:
    def __init__(self, func, take_request=False):
        self.func = func
        self.take_request = take_request
        self.request = None

    def set_request(self, request):
        self.request = request

    def __call__(self, *args, **kwargs):
        if self.take_request: args = (self.request,) + args
        return self.func(*args, **kwargs)
