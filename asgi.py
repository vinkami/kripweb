from .path import DNENode
from .request import Request


class AsgiApplication:
    def __init__(self, handler):
        self.handler = handler

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            node = self.handler.get_page(scope["path"])
            if isinstance(node, DNENode):
                return None
            view = node.views.get(scope["method"])
            body = await self.get_request_body(receive)

            request = Request()
            if body != b"":
                request.set_form_from_body(body)
            view.set_request(request)

            resp = await view()
            resp.set_handler(self.handler)
            await send(resp.head)
            await send(resp.body)
            resp.callback()

    @staticmethod
    async def get_request_body(receive):
        body = b''
        more_body = True

        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)

        return body
