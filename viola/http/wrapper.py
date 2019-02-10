class Wrapper(object):
    def __init__(self, data, env):
        self.data = data.decode("utf8")
        self.env = env

    def get_resp(self):
        # 200
        return """
HTTP/1.1 200 OK
Server: viola
Content-Type: application/json

{}
""".format(self.data)
