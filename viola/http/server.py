# encoding=utf8
import socket
from viola.event_loop import EventLoop
import fcntl
from viola.stream import Stream


class RouterEmptyException(Exception):
    pass


class HttpServer(object):

    def __init__(self, url_views):
        self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        flags = fcntl.fcntl(self.s_socket.fileno(), fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(self.s_socket.fileno(), fcntl.F_SETFD)
        self.s_socket.setblocking(0)
        self.s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.event_loop = EventLoop.instance()
        if not url_views:
            raise RouterEmptyException
        self.url_views = url_views

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
        try:
            c_socket, address = self.s_socket.accept()
        except:
            print("accept error, close it")
            c_socket.close()
            raise
        Stream(c_socket, self.event_loop, self.url_views)
