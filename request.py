from typing import Any


class Request:
    __slots__ = "form", "query_string", "host", "kwargs", "client", "method", "path", "http_version", "_scope"

    def __init__(self, scope):
        # Usually useful information
        self.form = {}
        self.query_string = {}
        self.host = ""
        self.kwargs = {}

        # Debug information
        self.client = f"{scope['client'][0]}:{scope['client'][1]}"
        self.method = scope['method']
        self.path = scope["path"] if scope["query_string"] == b"" else f"{scope['path']}?{scope['query_string'].decode()}"
        self.http_version = scope["http_version"]

        # Reference
        self._scope = scope

    @classmethod
    async def assemble(cls, scope, receive):
        request = cls(scope)

        # receive -> body -> form
        body = b''
        more_body = True
        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)

        if body != b"":
            request.set_form_from_body(body)

        request.set_query_string()
        request.set_host()
        return request

    def set_query_string(self):
        for data in self._scope["query_string"].decode().split("&"):
            if data.count("=") != 1: continue
            k, v = data.split("=")
            self.query_string[k] = v

    def set_form_from_body(self, body: bytes):
        body_str = body.decode()
        things = body_str.split("&")
        for t in things:
            k, v = t.split("=")
            self.form[k] = v

    def set_host(self):
        for item in self._scope["headers"]:
            if item[0] == b"host":
                self.host = item[1].decode()
                break

    def set_extra_url(self, arg_dict: dict[Any]):
        self.kwargs = arg_dict


class DummyRequest(Request):
    def __init__(self):
        scope = {'type': 'http', 'http_version': '1.1', 'asgi': {'spec_version': '2.1', 'version': '3.0'},
                 'method': 'GET', 'scheme': 'http', 'path': '/', 'raw_path': b'/', 'query_string': b'', 'root_path': '',
                 'headers': [(b'host', b'42.2.106.65'), (b'connection', b'keep-alive'), (b'cache-control', b'max-age=0'), (b'upgrade-insecure-requests', b'1'), (b'user-agent', b'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'), (b'accept', b'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'), (b'accept-encoding', b'gzip, deflate'), (b'accept-language', b'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'), (b'cp-extension-installed', b'Yes')],
                 'client': ('42.2.106.65', 50221), 'server': ('192.168.1.1', 80), 'extensions': {}}

        super(DummyRequest, self).__init__(scope)
