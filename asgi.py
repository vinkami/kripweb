from .path import DNENode, DummyNode
from .request import Request
from .response import Response, TextResponse, StaticResponse
from .error import NotResponseError, NoResponseReturnedError, NoMethodError, ResponseError
from .view import View
from queue import Empty as QueueEmpty
import asyncio


class AsgiApplication:
    def __init__(self, handler):
        self.handler = handler

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = await Request.assemble(scope, receive)

            ## URL -> Node -> View
            node, view = await self.get_node_view(request, scope)

            if view is not None:
                ## Node, View -> Queue -> Response
                resp_queue = self.view_to_response_queue(request, node, view)
                responses = await self.get_responses(resp_queue)

                try:
                    resp = responses[0]  # cannot handle more than 1 response yet
                except IndexError:
                    self.handler.logger.error(NoResponseReturnedError(f"No valid response is found when loading '{scope['path']}'"))
                    resp = await self.load_error_response("500", request)

            else:
                resp = await self.load_error_response("500", request)

            ## Response + checks -> Header, Body -> Send
            good_resp = await self.confirm_response(resp, request)
            await self.send_response(send, good_resp)

            # Logging
            if self.handler.setting.print_connection_information:
                self.handler.logger.info(self.handler.setting.app_logging_msg(request, good_resp))

    async def get_node_view(self, request, scope):
        if len(self.handler.setting.hosts_allowed) == 0 or request.host in self.handler.setting.hosts_allowed:
            # Check static url
            if scope["path"].find(self.handler.setting.static_url) == 0:
                path = scope["path"].split(self.handler.setting.static_url)[1]
                async def func(): return StaticResponse(path)
                return DummyNode(), View(func)

            # Get view from pages
            node = self.handler.get_page(scope["path"])
            if isinstance(node, DNENode):
                view = self.load_error_view("404")
            else:
                view = node.views.get(scope["method"])
                if view is None:
                    self.handler.logger.error(NoMethodError(f"There is no {scope['method']} method for {node.get_full_url_of_self()}"))
                    view = await self.load_error_view("501")
            return node, view

        return DummyNode(), await self.load_error_view("bad_host")

    def view_to_response_queue(self, request, node, view):
        request.set_extra_url(node.kwargs)
        node.kwargs = {}
        view.set_request(request)
        view.set_await_send(self.handler.setting.await_send_mode)
        return view()

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
                if r is not None: responses.append(r)  # ignore None in non-returning functions
        return responses

    async def confirm_response(self, resp, request):
        if not isinstance(resp, Response):
            self.handler.logger.warning(NotResponseError(
                f"The returning object ({resp}) is not a Response object when loading '{scope['path']}'"))
            resp = TextResponse(str(resp))

        try:
            resp.set_handler(self.handler)
        except ResponseError as e:
            if isinstance(e.error_response, StaticResponse):
                # Triggered when someone tried to load a static page that does not exist with direct url
                resp = await self.load_error_response("404", request)
            else:
                # idk when it will be triggered. Just leave as a safeguard
                resp = await self.load_error_response("502", request)
                self.handler.logger.error(e)
        return resp

    async def load_error_response(self, error_code, request):
        view = await self.load_error_view(error_code)
        responses = await self.get_responses(self.view_to_response_queue(request, DummyNode(), view))
        return responses[0]

    async def load_error_view(self, error_code):
        node = self.handler.error_pages.get_node(str(error_code))
        return node.views.get("GET")

    @staticmethod
    async def send_response(send, resp):
        await send(resp.head)
        await send(resp.body)

        if resp.callback_be_awaited:
            await resp.callback()
        else:
            resp.callback()
