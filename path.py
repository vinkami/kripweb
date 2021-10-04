from .error import NoMethodError
from .view import View
from .response import TextResponse
from .constant import ErrorCode


class Node:
    def __init__(self, url_part, views, name):
        self.url = url_part
        self.views = views        # self.views = {"GET": ..., "POST": ...}
        self.children = []
        self.parent = None
        self.kwargs = {}          # kwargs that will be used when called
        self.name = name

    def add_child(self, node):
        self.children.append(node)
        node.parent = self

    def get_node(self, url):
        if url in ("", "/"): return self

        url = url.split("/")
        if url[0] == "": url.pop(0)

        if len(url) == 1:
            url_part = url[0]
            for node in self.children:
                if node.url == url_part:
                    node.kwargs.update(self.kwargs)
                    self.kwargs = {}
                    return node

            for node in self.children:  # check for wildcards
                if node.url[0] == "<" and node.url[-1] == ">":
                    node.kwargs.update(self.kwargs)
                    node.kwargs.update({node.url[1:-1]: url_part})
                    self.kwargs = {}
                    return node

            return DNENode(url_part, self)

        elif len(url) >= 2:
            url_part = url.pop(0)
            node = self.get_node(url_part)
            if isinstance(node, DNENode): return node.add_children_parts(url_part, *url)
            return node.get_node("/".join(url))

    def get_GET_view(self, url):
        return self.get_node(url).views.get("GET")

    def add_view(self, method, view):
        self.views[method] = view

    def __iter__(self):
        return iter(self.children)

    def __repr__(self):
        return f"<Page name='{self.name}' url='{self.get_full_url_of_self()}'>"

    def get_full_url_of_self(self):
        url = [self.url]
        p = self.parent
        while p is not None:
            url.append(p.url)
            p = p.parent

        url.reverse()
        return "/".join(url)


class DNENode(Node):
    def __init__(self, url_part, parent_node):
        super().__init__(url_part, None, "DNE")
        self.parent = parent_node
        self.children_parts = []

    def __call__(self, *args, **kwargs):
        raise NoMethodError("Nodes that do not exist have no methods to call")

    def add_children_parts(self, *url_parts):
        for part in url_parts:
            self.children_parts.append(part)
        return self


class MasterNode(Node):
    def __init__(self):
        super().__init__("", {}, "")

    def handle_new_view(self, url="", method="GET", take_request=False, name=""):
        def inner(func):
            if isinstance(node := self.get_node(url), DNENode):
                urls = url.split("/")
                node = self
                for u in urls:
                    next_node = node.get_node(u)
                    if isinstance(next_node, DNENode):
                        node_name = str(name) if name != "" else func.__name__
                        node.add_child(Node(u, {}, node_name))
                        node = node.get_node(u)
                inner(func)
            else:
                node.add_view(method.upper(), View(func, take_request))

            return func
        return inner


class DummyNode(Node):
    def __init__(self):
        super().__init__("", {}, "")

    def __repr__(self):
        return "<DummyNode>"


class ErrorMasterNode(MasterNode):
    def __init__(self):
        super().__init__()
        self.handle_new_view("404", name="404")(self.NotFound404)
        self.handle_new_view("500", name="500")(self.InternalServerError500)
        self.handle_new_view("502", name="502")(self.BadGateway502)
        self.handle_new_view("bad_host", name="bad_host")(self.BadHost)
        self.handle_new_view("501", name="501")(self.NotImplemented501)

    # Decorator for adding default errors
    def new_error_view(self, url, name=None):
        def inner(func):
            if name is None: name = url
            self.handle_new_view(str(url), name=str(name))(func)
            return func
        return inner


    # Default responses for errors down here. Will be replaced when redefined with @handler.error_page()
    @staticmethod
    async def NotFound404():
        resp = TextResponse("404 Not Found")
        resp.status_code, resp.status = ErrorCode.get(404)
        return resp

    @staticmethod
    async def InternalServerError500():
        resp = TextResponse("500 Internal Server Error")
        resp.status_code, resp.status = ErrorCode.get(500)
        return resp

    @staticmethod
    async def BadGateway502():
        resp = TextResponse("502 Bad gateway")
        resp.status_code, resp.status = ErrorCode.get(502)
        return resp

    @staticmethod
    async def BadHost():
        resp = TextResponse("This host name is not allowed")
        resp.status_code, resp.status = ErrorCode.get("bad_host")
        return resp

    @staticmethod
    async def NotImplemented501():
        resp = TextResponse("501 Not Implemented")
        resp.status_code, resp.status = ErrorCode.get(501)
        return resp
