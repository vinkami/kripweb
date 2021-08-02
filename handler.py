from .setting import Setting
from .asgi import AsgiApplication
from .path import MasterNode
from .error import NotHandlerError, NothingMatchedError


class HandlerBase:
    def __init__(self):
        self.pages = MasterNode()
        self.page = self.pages.handle_new_view  # Decorator to add page

    def get_all_pages(self):
        def add_pages_of(page):
            pages = []
            for p in page:
                pages += [p, *add_pages_of(p)]
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

    def name_to_url(self, page_name, from_subpages=""):
        if from_subpages == "":
            # View is in main script
            for node in self.get_all_pages():
                if node.name == page_name:
                    return f"/{node.get_full_url_of_self()}"
        else:
            # View is in other scripts
            for subpages in self.subpageses:
                if subpages.name == from_subpages:
                    for node in subpages.get_all_pages():
                        if node.name == page_name:
                            return f"/{subpages.url}/{node.url}"

                    else:
                        # View not found in the subpages
                        raise NothingMatchedError(f"No page named '{page_name}' is found in subpages '{from_subpages}'")
            else:
                # Subpages not found
                raise NothingMatchedError(f"No subpages is named '{from_subpages}'")


class PagesHandler(HandlerBase):
    def __init__(self, name, url):
        super().__init__()
        self.name = name
        self.url = url
        self.get_page = self.pages.get_node

    def __repr__(self):
        return f"<Subpages name='{self.name}' url='{self.url}'>"
