# encoding=utf8
from viola.event_loop import EventLoop
from viola.http_server import HttpServer
import json


resp_data = b"""
HTTP/1.1 200 OK

{"result": "ok"}
"""

# Mock web framework
router = {}


def get(request, response):
    # print("[headers]", request.headers)
    # for k, v in request.headers.items():
    #     print(k + ':', v)
    response.write(resp_data)


def post(*args, **kwargs):
    pass


router["/listNews"] = get
router["/xxx"] = post


if __name__ == '__main__':
    server = HttpServer(router)    # 这个 router 的传递路线值得慢慢体会, 理解面向对象之间的通信方式
    server.bind(host="10.211.55.25", port=2333)
    server.listen()
    event_loop = EventLoop.instance()
    event_loop.start()
