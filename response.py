class Response:
    def __init__(self):
        self.body_content = ""
        self.headers = []
        self.callback = lambda: None

    @property
    def head(self):
        return {
            'type': 'http.response.start',
            'status': 200,
            'headers': self.headers
        }

    @property
    def body(self):
        return {
            'type': 'http.response.body',
            'body': self.body_content
        }


class TextResponse(Response):
    def __init__(self, text: str):
        super().__init__()
        self.headers.append([b"content-type", b"text/plain"])
        self.body_content = text.encode()
