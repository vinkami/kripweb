from .path import DNENode


class AsgiApplication:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            node = self.app.get_page(scope["path"])
            if isinstance(node, DNENode):
                return None
            view = node.views.get(scope["method"])

            resp = view()

            await send(resp.head)
            await send(resp.body)
            resp.callback()
