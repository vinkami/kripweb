class Request:
    def __init__(self, scope):
        self.form = {}
        self.query_string = {}
        self.host = ""

        self.scope = scope
        self.set_query_string()

    def set_query_string(self):
        for data in self.scope["query_string"].decode().split("&"):
            if data.find("=") != 1: continue
            k, v = data.split("=")
            self.query_string[k] = v

    def set_form_from_body(self, body: bytes):
        body = body.decode()
        things = body.split("&")
        for t in things:
            k, v = t.split("=")
            self.form[k] = v

