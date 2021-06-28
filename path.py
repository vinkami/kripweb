from .error import NoMethodError


class Node:
    def __init__(self, url_part, views):
        self.url = url_part
        self.views = views        # self.views = {"GET": ..., "POST": ...}
        self.children = []
        self.parent = None

    def __call__(self, method="GET", *args, **kwargs):
        return self.views[method.upper()](*args, **kwargs)

    def add_child(self, node):
        self.children.append(node)
        node.parent = self

    def get_node(self, url):
        if url in ["", "/"]: return self

        url = url.split("/")
        if url[0] == "": url.pop(0)

        if len(url) == 1:
            url_part = url[0]
            for node in self.children:
                if node.url == url_part:
                    return node
            return DNENode(url_part, self)

        elif len(url) >= 2:
            node = self.get_node(url.pop(0))
            if isinstance(node, DNENode): return node
            return node.get_node("/".join(url))

    def add_view(self, method, view):
        self.views[method] = view


class DNENode(Node):
    def __init__(self, url_part, parent_node):
        super().__init__(url_part, None)
        self.parent = parent_node

    def __call__(self, *args, **kwargs):
        raise NoMethodError("Nodes that do not exist have no methods to call")
