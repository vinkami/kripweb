from jinja2 import Environment, FileSystemLoader


class Setting:
    def __init__(self):
        self.__template_path = None
        self.__static_path = None

        self.jinja2_env = Environment()

    @property
    def template_path(self): return self.__template_path

    @property
    def static_path(self): return self.__static_path

    def set_template_path(self, path):
        self.__template_path = path
        self.jinja2_env.loader = FileSystemLoader(self.__template_path)

    def set_static_path(self, path):
        self.__static_path = path
