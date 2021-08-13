from jinja2 import Environment, FileSystemLoader, select_autoescape


class Setting:
    def __init__(self,
                 template_path="template/",
                 static_path="static/", static_url="/static/",
                 await_send=False,
                 hosts_allowed=None,
                 print_conn_info=True):

        self.jinja2_env = Environment(autoescape=select_autoescape())

        self.__template_path = self.set_template_path(template_path)
        self.__static_path = self.set_static_path(static_path)
        self.__static_url = self.set_static_url(static_url)
        self.__await_send = self.toggle_await_send_mode(await_send)
        self.__hosts_allowed = hosts_allowed or []
        self.__print_conn_info = self.toggle_print_conn_info(print_conn_info)

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

    @property
    def print_connection_information(self): return self.__print_conn_info

    def set_template_path(self, path: str) -> str:
        if path[0] == "/": path = path[1:]
        if path[-1] != "/": path = path + "/"
        self.__template_path = path
        self.jinja2_env.loader = FileSystemLoader(self.__template_path)
        return path

    def set_static_path(self, path: str) -> str:
        if path[0] == "/": path = path[1:]
        if path[-1] != "/": path = path + "/"
        self.__static_path = path
        return path

    def toggle_await_send_mode(self, state: bool=None) -> bool:
        if state is None: self.__await_send = not self.__await_send
        else: self.__await_send = state
        return self.__await_send

    def allow_host(self, *hostnames: str) -> list:
        for hostname in hostnames:
            if hostname in self.__hosts_allowed: return self.__hosts_allowed
            self.__hosts_allowed.append(hostname)
        return self.__hosts_allowed

    def set_static_url(self, url: str) -> str:
        if url[0] != "/": url = "/" + url
        if url[-1] != "/": url = url + "/"
        self.__static_url = url
        return url

    def toggle_print_conn_info(self, state: bool=None) -> bool:
        if state is None: self.__print_conn_info = not self.__print_conn_info
        else: self.__print_conn_info = state
        return self.__print_conn_info
