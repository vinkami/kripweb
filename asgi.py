from .path import DNENode
from .request import Request
from .response import Response, TextResponse
from .error import NotResponseError


class AsgiApplication:
    def __init__(self, handler):
        self.handler = handler

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Set up the request
            request = Request(scope)
            body = await self.get_request_body(receive)
            if body != b"":
                request.set_form_from_body(body)

            # Get the view
            node = self.handler.get_page(scope["path"])
            if isinstance(node, DNENode):
                view = self.handler.error_pages.get(404)
            else:
                view = node.views.get(scope["method"])

            # Do the thing
            view.set_request(request)
            resp = await view(**node.kwargs)
            if not isinstance(resp, Response):
                print(NotResponseError(f"The returning object ({resp}) is not a Response object when loading '{scope['path']}'"))
                resp = TextResponse(str(resp))
            node.kwargs = {}
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
