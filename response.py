from .error import NotSetError


class Response:
    def __init__(self):
        self.body_content = b""         # needs to be encoded when set
        self.headers = {}               # bytes key and value
        self.cookies = {}               # string key and value
        self.content_type = ""          # will be encoded later
        self.callback = lambda: None    # things that needs to be done after or only after responding
        self.handler = None             # will be set in the application class

    @property
    def head(self):
        if self.content_type == "": raise NotSetError("Content type is not set")
        self.headers[b"content-type"] = self.content_type.encode()
        return {
            'type': 'http.response.start',
            'status': 200,
            'headers': [[k, v] for k, v in self.headers.items()]
                     + [[b"set-cookie", f"{k}={v}".encode()] for k, v in self.cookies.items()]
        }

    @property
    def body(self):
        return {
            'type': 'http.response.body',
            'body': self.body_content
        }

    def set_handler(self, handler):
        self.handler = handler
        return self

    def set_cookie(self, key, value):
        self.cookies[key] = value
        return self

    def set_callback(self, func, *args, **kwargs):
        self.callback = lambda: func(*args, **kwargs)
        return self


class TextResponse(Response):
    def __init__(self, text: str):
        super().__init__()
        self.content_type = "text/plain"
        self.body_content = str(text).encode()


class ImageResponse(Response):
    def __init__(self, image: bytes, fmt: str="png"):
        super().__init__()
        self.content_type = f"image/{fmt}"
        self.body_content = image


class FileResponse(Response):
    def __init__(self, path, filename, as_attachemnt=False):
        super().__init__()
        self.content_type = "application/octet-stream"
        self.headers[b"content-disposition"] = f"{'attachment' if as_attachemnt else 'inline'}; filename={filename}".encode()
        with open(path, "rb") as f:
            self.body_content = f.read()


class StaticResponse(Response):
    def __init__(self, path):
        super().__init__()
        self.content_type = "application/octet-stream"
        self.path = path

    def set_handler(self, handler):
        super().set_handler(handler)
        self.headers[b"content-disposition"] = b"inline"
        with open(self.handler.setting.static_path + self.path, "rb") as f:
            self.body_content = f.read()


class HTMLResponse(Response):
    def __init__(self, html=""):
        super().__init__()
        self.body_content = html.encode()
        self.content_type = "text/html"
        self.path = None
        self.variables = {}

    @classmethod
    def render(cls, path, **variables):
        self = cls()
        self.path = path
        self.variables = variables
        return self

    def set_handler(self, handler):
        super().set_handler(handler)
        if self.path:
            self.body_content = self.handler.setting.jinja2_env.get_template(self.path).render(**self.variables).encode()
