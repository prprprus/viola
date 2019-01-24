# encoding=utf8
import socket
from viola.event_loop import EventLoop
import fcntl
from viola.stream import Stream


class RouterEmptyException(Exception):
    pass


class HttpServer(object):

    def __init__(self, router):
        self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        flags = fcntl.fcntl(self.s_socket.fileno(), fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(self.s_socket.fileno(), fcntl.F_SETFD)
        self.s_socket.setblocking(0)
        self.s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.event_loop = EventLoop.instance()
        if not router:
            raise RouterEmptyException
        self.router = router

    def bind(self, host="localhost", port=80):
        self.s_socket.bind((host, port))

    def listen(self, size=128):
        self.s_socket.listen(size)
        self.start()    # httpserver start here

    def start(self):
        self.event_loop.add_handler(self.s_socket.fileno(), EventLoop.READ,
                                    self.handle_event)

    def stop(self):
        pass

    def handle_event(self, fd, event):
        # 这里必须要 `accept()` 不然水平触发会一直通知. CPU 使用会狂飙
        try:
            c_socket, address = self.s_socket.accept()
        except:
            print("accept error, close it")
            c_socket.close()
            raise
        Stream(c_socket, self.event_loop, self.router)
