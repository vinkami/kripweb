from .error import NotSetError, ResponseError
from .constant import ErrorCode


class Response:
    def __init__(self):
        self.body_content = b""             # needs to be encoded when set
        self.headers = {}                   # bytes key and value
        self.status_code = 200
        self.status = "OK"
        self.cookies = {}                   # string key and value
        self.content_type = ""              # will be encoded later
        self.callback = lambda: None
        self.callback_be_awaited = False
        self.handler = None                 # will be set in the application class

    @property
    def head(self):
        if self.content_type == "": raise NotSetError("Content type is not set")
        self.headers[b"content-type"] = self.content_type.encode()
        return {
            'type': 'http.response.start',
            'status': self.status_code,
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
        self.extra_work()

    def set_cookie(self, key, value):
        self.cookies[key] = value

    def set_callback(self, func, *args, be_awaited=False, **kwargs):
        self.callback = lambda: func(*args, **kwargs)
        self.callback_be_awaited = be_awaited
        return self

    def extra_work(self):
        pass


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
        self.headers[b"content-disposition"] = f"{'attachment' if as_attachemnt else 'inline'}; filename='{filename}'".encode()
        with open(path, "rb") as f:
            self.body_content = f.read()


class StaticResponse(Response):
    def __init__(self, path):
        super().__init__()
        self.content_type = "application/octet-stream"
        self.path = path

    def extra_work(self):
        self.headers[b"content-disposition"] = b"inline"
        try:
            with open(path := (self.handler.setting.static_path + self.path), "rb") as f:
                self.body_content = f.read()
        except OSError:
            raise ResponseError(f"Cannot resolve path \"{path}\"", self)


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

    def extra_work(self):
        if self.path:
            self.body_content = self.handler.setting.jinja2_env.get_template(self.path).render(**self.variables).encode()


class Redirect(Response):
    def __init__(self, url=""):
        super().__init__()
        self.content_type = "text/html"
        self.status_code = 302
        self.status = "Found"
        self.url = url

        self.page_name = None
        self.from_subpages = None

    @classmethod
    def to_view(cls, page_name, from_subpages=""):
        self = cls()
        self.page_name = page_name
        self.from_subpages = from_subpages
        return self

    def extra_work(self):
        url = self.url if self.page_name is None else self.handler.name_to_url(self.page_name, self.from_subpages)
        self.status = f"Redirected to {url}"
        self.body_content = f"<script>window.location.replace('{url}')</script>".encode()


def errorize(resp: Response, error_code: (int or str)) -> Response:
    resp.status_code, resp.status = ErrorCode.get(error_code)
    return resp
