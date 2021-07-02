class ErrorBase(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.msg


class NoMethodError(ErrorBase):
    pass


class NotSetError(ErrorBase):
    pass


class NotResponseError(ErrorBase):
    pass
