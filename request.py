class Request:
    def __init__(self):
        self.form = {}

    def set_form_from_body(self, body: bytes):
        body = body.decode()
        things = body.split("&")
        for t in things:
            k, v = t.split("=")
            self.form[k] = v
