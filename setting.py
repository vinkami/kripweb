from jinja2 import Environment, FileSystemLoader


class Setting:
    def __init__(self):
        self.__template_path = "template/"
        self.__static_path = "static/"
        self.__static_url = "/static/"
        self.__await_send = False
        self.__hosts_allowed = []

        self.jinja2_env = Environment(loader=FileSystemLoader(self.__template_path))

    @property
    def template_path(self): return self.__template_path

    @property
    def static_path(self): return self.__static_path

    @property
    def await_send_mode(self): return self.__await_send

    @property
    def hosts_allowed(self): return self.__hosts_allowed

    @property
    def static_url(self): return self.__static_url

    def set_template_path(self, path: str) -> None:
        if path[0] == "/": path = path[1:]
        if path[-1] != "/": path = path + "/"
        self.__template_path = path
        self.jinja2_env.loader = FileSystemLoader(self.__template_path)

    def set_static_path(self, path: str) -> None:
        if path[0] == "/": path = path[1:]
        if path[-1] != "/": path = path + "/"
        self.__static_path = path

    def toggle_await_send_mode(self, state: bool=None) -> None:
        if state is None: self.__await_send = not self.__await_send
        else: self.__await_send = state

    def allow_host(self, *hostnames: str) -> None:
        for hostname in hostnames:
            if hostname in self.__hosts_allowed: return
            self.__hosts_allowed.append(hostname)

    def set_static_url(self, url: str) -> None:
        if url[0] != "/": url = "/" + url
        if url[-1] != "/": url = url + "/"
        self.__static_url = url
