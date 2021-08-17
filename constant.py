class ErrorCode:
    code_to_msg = {404: "Not Found", 500: "Error Occured", 502: "Response is janky", 403: "Forbidden", 501: "No Method"}

    @classmethod
    def get(cls, error_code):
        if error_code == "bad_host": error_code = 403

        return error_code, cls.code_to_msg.get(error_code)


def app_logging_message(request, response):
    return f"Connection:  {request.client} -> {request.host} - " \
           f"{request.method} {request.path} using HTTP/{request.http_version} - " \
           f"{response.status_code} {response.status}"
