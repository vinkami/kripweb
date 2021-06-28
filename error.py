class NoMethodError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.msg


class NotSetError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.msg
