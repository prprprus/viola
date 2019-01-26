# encoding=utf8
"""
- 将 stream 读到的数据解析并封装成 `HttpRequest` 对象
- 将 web-framework 的返回数据封装成 `HttpResponse` 并交给 stream 写
"""
from viola.http.request import HttpRequest
from viola.http.response import HttpResponse


class HttpHandler(object):

    def __init__(self, stream, event_loop, url_views):
        self.stream = stream
        self.event_loop = event_loop
        self.url_views = url_views

    def route(self):
        """路由"""
        request = HttpRequest(self.stream.read_buffer)
        response = HttpResponse(self.stream, self.event_loop)
        self.url_views[request.headers["url"]](request, response)
