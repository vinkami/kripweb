from .setting import Setting
from .asgi import AsgiApplication
from .path import MasterNode
from .error import NotHandlerError


class HandlerBase:
    def __init__(self):
        self.pages = MasterNode()
        self.page = self.pages.handle_new_view  # Decorator to add page

    def get_all_pages(self):
        def add_pages_of(page):
            pages = []
            for p in page:
                pages.append(p)
                pages.append(*add_pages_of(p))
            return pages

        return [self.pages, *add_pages_of(self.pages)]


class Handler(HandlerBase):
    def __init__(self, setting: Setting=None):
        super().__init__()
        self.setting = setting or Setting()
        self.error_pages = MasterNode()
        self.subpageses = []

    def get_application(self):
        return AsgiApplication(self)

    def get_page(self, url: str):
        for subpages in self.subpageses:
            if url.find(subpages.url) == 1:
                remaining_url = url.split(subpages.url)[1]
                return subpages.get_page(remaining_url)

        return self.pages.get_node(url)

    def error_page(self, err_code="404", take_request=False):
        def inner(func):
            self.error_pages.handle_new_view(str(err_code), "GET", take_request)(func)
            return func
        return inner

    def ingest_subhandler(self, subhandler):
        if not isinstance(subhandler, HandlerBase):
            raise NotHandlerError(f"The given object to ingest ({str(subhandler)}) is not a handler")
        self.subpageses.append(subhandler)


class PagesHandler(HandlerBase):
    def __init__(self, name, url):
        super().__init__()
        self.name = name
        self.url = url
        self.get_page = self.pages.get_node

    def __repr__(self):
        return f"<Subpages name='{self.name}' url='{self.url}'>"
