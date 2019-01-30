# encoding=utf8
"""
# web-framework 部分
- 将 stream 读到的数据解析并封装成 `HttpRequest` 对象
- 将 web-framework 的返回数据封装成 `HttpResponse` 并交给 stream 写
"""
from viola.http.request import HttpRequest
from viola.http.response import HttpResponse


class HttpHandler(object):

    def __init__(self, stream, event_loop, url_views, http_req):
        self.stream = stream
        self.event_loop = event_loop
        self.url_views = url_views
        self.http_req = http_req
        self.route()

    def route(self):
        request = HttpRequest(self.http_req)
        response = HttpResponse(self.stream, self.event_loop)
        self.url_views[request.headers["url"]](request, response)
