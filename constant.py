class ErrorCode:
    code_to_msg = {404: "Not Found", 500: "Error Occured", 502: "Response is janky", 403: "Forbidden", 501: "No Method"}

    @classmethod
    def get(cls, error_code):
        if error_code == "bad_host": error_code = 403

        return error_code, cls.code_to_msg.get(error_code)
