from .path import DNENode
from .request import Request
from .response import Response, TextResponse
from .error import NotResponseError, ErrorPageNotSetError, NoResponseReturnedError
from queue import Empty as QueueEmpty
import asyncio


class AsgiApplication:
    def __init__(self, handler):
        self.handler = handler

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "https"):
            # Set up the request
            request = await self.assemble_request(scope, receive)

            # Check allowed host
            node = type("Node", (), {"kwargs": {}})()  # Such that view(**node.kwargs) will not hang if no nodes found
            if len(self.handler.setting.hosts_allowed) == 0 or request.host in self.handler.setting.hosts_allowed:
                # Get the view
                node = self.handler.get_page(scope["path"])
                if isinstance(node, DNENode):
                    view = self.handler.error_pages.get(404)
                    if view is None: raise ErrorPageNotSetError("The error 404 page is not found when handling not-found urls")
                else:
                    view = node.views.get(scope["method"])
            else:
                view = self.handler.error_pages.get("bad_host")
                if view is None: raise ErrorPageNotSetError("The bad_host error page is not found when a disallowed host is found")

            # View -> Resp
            view.set_request(request)
            view.set_await_send(self.handler.setting.await_send_mode)
            resp_queue = view(**node.kwargs)

            # Get all responses from the resp_queue, which actually contains asyncio tasks
            responses = []
            while True:
                try:
                    task = resp_queue.get(block=False)
                except QueueEmpty:
                    break
                else:
                    while not task.done(): await asyncio.sleep(0.001)
                    r = task.result()
                    if r is not None: responses.append(r)  # non-returning function calls have None-type object as a return

            try:
                resp = responses[0]
            except IndexError:
                raise NoResponseReturnedError(f"No valid response is found when loading '{scope['path']}'")

            if not isinstance(resp, Response):
                # Print the error because it's non-fatal
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

    async def assemble_request(self, scope, receive):
        request = Request(scope)

        # Request body
        body = await self.get_request_body(receive)
        if body != b"":
            request.set_form_from_body(body)

        # Set host
        for item in scope["headers"]:
            if item[0] == b"host":
                request.host = item[1].decode()
                break

        return request
