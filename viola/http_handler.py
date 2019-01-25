# encoding=utf8
import io
from viola.event_loop import EventLoop


class HttpHandler(object):
    def __init__(self, stream, event_loop, router):
        self.stream = stream
        self.event_loop = event_loop
        self.router = router
        self.headers = {}
        self.env = {}
        # self.parse_http_request()
        self.execute()

    def parse_http_request(self):
        self._parse_headers()
        self._parse_arguments()
        self._parse_body()
        self._parse_mime_body()

    def _parse_headers(self):
        req_cont = io.StringIO(self.stream.read_buffer.popleft().decode("utf8"))
        for line in req_cont.readlines():
            line = line.strip('\n')
            if line:
                # 解析 HTTP headers 的第一行
                if ':' not in line:
                    rows = line.split(' ')
                    self.headers["method"] = rows[0]
                    self.headers["url"] = rows[1]
                    self.headers["version"] = rows[2]
                # 解析 HTTP headers 的其余行
                else:
                    key, value = line.split(': ')
                    self.headers[key.strip()] = value.strip()
        self.env["headers"] = self.headers

    def _parse_arguments(self):
        pass

    def _parse_body(self):
        pass

    def _parse_mime_body(self):
        pass

    def execute(self):
        """路由"""
        request = HttpRequest(self.headers, self.env)
        response = HttpResponse(self.stream, self.event_loop)
        # self.router[request.headers["url"]](request, response)
        self.router["/listNews"](request, response)


class HttpRequest(object):
    def __init__(self, headers, env):
        self.headers = headers
        self.env = env


class HttpResponse(object):
    def __init__(self, stream, event_loop):
        self.stream = stream
        self.event_loop = event_loop

    def write(self, resp_data):
        # 封装 data => HTTP 响应体格式
        # 写到 stream 的 write_buffer
        # 将 stream.c_socket 的监听事件修改成 EventLoop.WRITE
        self.stream.write_buffer.append(resp_data)
        events = EventLoop.WRITE
        self.event_loop.update_handler(self.stream.c_socket.fileno(), events)
