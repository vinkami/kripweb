class WsgiApplication:
    def __init__(self, app):
        self.app = app

    def __call__(self, scope, receive, send):
        pass
