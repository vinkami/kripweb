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


class NoResponseReturnedError(ErrorBase):
    pass


class NotSubhandlerError(ErrorBase):
    pass


class NothingMatchedError(ErrorBase):
    pass


class ResponseError(ErrorBase):
    def __init__(self, msg, error_response):
        super().__init__(msg)
        self.error_response = error_response


class SettingError(ErrorBase):
    def __init__(self, msg, erf):
        super().__init__(msg)
        self.erf = erf

    def __repr__(self):
        return f"{self.erf} -- {self.msg}"
