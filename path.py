from .error import NoMethodError
from .view import View


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
                        node_name = name or func.__name__
                        node.add_child(Node(u, {}, node_name))
                        node = node.get_node(u)
                inner(func)
            else:
                node.add_view(method.upper(), View(func, take_request))

            return func
        return inner
