from .path import DNENode
from .request import Request
from .response import Response, TextResponse, StaticResponse
from .error import NotResponseError, ErrorPageNotSetError, NoResponseReturnedError, NoMethodError, ResponseError
from .view import View
from queue import Empty as QueueEmpty
import asyncio


class AsgiApplication:
    def __init__(self, handler):
        self.handler = handler

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "https"):
            # Set up the request
            request = await Request.assemble(scope, receive)

            # Check allowed host
            if len(self.handler.setting.hosts_allowed) == 0 or request.host in self.handler.setting.hosts_allowed:
                node, view = self.get_node_view(scope)
            else:
                view = self.handler.error_pages.get_GET_view("bad_host")
                if view is None: raise ErrorPageNotSetError("The bad_host error page is not found when a disallowed host is found")

            # View -> Resp
            request.set_extra_url(node.kwargs)
            node.kwargs = {}
            view.set_request(request)
            view.set_await_send(self.handler.setting.await_send_mode)
            resp_queue = view()

            # Get all responses from the resp_queue, which actually contains asyncio tasks
            responses = await self.get_responses(resp_queue)
            try:
                resp = responses[0]  # cannot handle more than 1 response yet
            except IndexError:
                raise NoResponseReturnedError(f"No valid response is found when loading '{scope['path']}'")

            # Send the response and do the callback
            if not isinstance(resp, Response):
                # Print the error because it's non-fatal
                print(NotResponseError(f"The returning object ({resp}) is not a Response object when loading '{scope['path']}'"))
                resp = TextResponse(str(resp))

            try:
                resp.set_handler(self.handler)
            except ResponseError as e:
                if isinstance(e.error_response, StaticResponse):  # Might be someone trying to load a non-existing static file by url
                    resp = TextResponse("404 Not Found")
                else:
                    raise e
            await send(resp.head)
            await send(resp.body)
            if resp.callback_be_awaited:
                await resp.callback()
            else:
                resp.callback()

    def get_node_view(self, scope):
        # Check static url
        if scope["path"].find(self.handler.setting.static_url) == 0:
            path = scope["path"].split(self.handler.setting.static_url)[1]
            async def func(): return StaticResponse(path)
            return View(func)

        # Get view from pages
        node = self.handler.get_page(scope["path"])
        if isinstance(node, DNENode):
            view = self.handler.error_pages.get_GET_view("404")
            if view is None: raise ErrorPageNotSetError("The error 404 page is not found when handling not-found urls")
        else:
            view = node.views.get(scope["method"])
            if view is None: raise NoMethodError(
                f"There is no {scope['method']} method for {node.get_full_url_of_self()}")
        return node, view

    @staticmethod
    async def get_responses(resp_queue):
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
        return responses
