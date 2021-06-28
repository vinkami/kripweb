class WsgiApplication:
    def __init__(self, handler):
        self.handler = handler

    def __call__(self, scope, receive, send):
        pass
