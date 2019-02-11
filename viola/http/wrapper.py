class Wrapper(object):
    def __init__(self, data, env):
        self.data = data.decode("utf8")
        self.env = env

    def get_resp(self):
        # Note: Nginx add additional response headers if and only if
        # format of response accord with HTTP protocol
        # 200
        return "HTTP/1.1 200 OK\r\nContent-Length: {0}\r\n\r\n{1}" \
            .format(len(self.data), self.data)
        # 500: TODO
        pass
