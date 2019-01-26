# encoding=utf8
import io
from viola.event_loop import EventLoop


class HTTPMethodException(Exception):
    pass


class HTTPVersionException(Exception):
    pass


class HttpHandler(object):

    HTTP_METHOD = [
        "OPTIONS",
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "TRACE",
        "CONNECT"
    ]
    HTTP_VERSION = ["HTTP/1.1", "HTTP/1.0"]

    def __init__(self, stream, event_loop, router):
        self.stream = stream
        self.event_loop = event_loop
        self.router = router
        self.headers = {}
        self.env = {}
        self.parse_request()
        self.execute()

    def parse_request(self):
        self._parse_headers()
        self._parse_body()
        self._parse_mime_body()

    def _parse_headers(self):
        req_cont = io.StringIO(self.stream.read_buffer.popleft().decode("utf8"))
        for line in req_cont.readlines():
            line = line.strip('\n').strip('\r')
            if line:
                # 解析 HTTP headers 的第一行
                if ':' not in line:
                    rows = line.split(' ')
                    self._parse_method(rows[0])
                    self._parse_arguments(rows[1])
                    self._parse_version(rows[2])
                else:
                    key, value = line.split(': ')
                    self.headers[key.strip()] = value.strip()
        self.env["headers"] = self.headers

    def _parse_method(self, method):
        """解析请求方法"""
        if method not in HttpHandler.HTTP_METHOD:
            raise HTTPMethodException
        self.headers["method"] = method

    def _parse_arguments(self, url):
        """解析参数并将参数转成字典形式"""
        if '?' not in url:
            self.headers["url"] = url
        else:
            self.headers["url"] = url.split('?')[0]
            args = [arg for arg in url.split('?')[1].split('&')]
            self.headers["arguments"] = \
                {arg.split('=')[0]: arg.split('=')[1] for arg in args}

    def _parse_version(self, version):
        """解析 HTTP 版本"""
        if version not in HttpHandler.HTTP_VERSION:
            raise HTTPVersionException
        self.headers["version"] = version

    def _parse_body(self):
        pass

    def _parse_mime_body(self):
        pass

    def execute(self):
        """路由"""
        request = HttpRequest(self.headers, self.env)
        response = HttpResponse(self.stream, self.event_loop)
        self.router[request.headers["url"]](request, response)


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
        self.wrapper_response(resp_data)
        self.stream.write_buffer.append(resp_data)
        events = EventLoop.WRITE
        self.event_loop.update_handler(self.stream.c_socket.fileno(), events)

    def wrapper_response(sefl, resp_data):
        pass
