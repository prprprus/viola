# encoding=utf8
from viola.event_loop import EventLoop


class HttpResponse(object):
    def __init__(self, stream, event_loop):
        self.stream = stream
        self.event_loop = event_loop

    def write(self, resp_data):
        # 封装 data => HTTP 响应体格式
        # 写到 stream 的 write_buffer
        # 将 stream.c_socket 的监听事件修改成 EventLoop.WRITE
        # Addition: 超过 SNDBUF 的不给发
        self.wrapper_response(resp_data)
        self.stream.write_buffer.append(resp_data)
        events = EventLoop.WRITE
        self.event_loop.update_handler(self.stream.c_socket.fileno(), events)

    def wrapper_response(sefl, resp_data):
        pass


class HttpStatusResponse(object):
    """404, 405..."""
    pass
