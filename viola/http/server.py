# encoding=utf8
import socket
from viola.event_loop import EventLoop
import fcntl
from viola.stream import Stream
import os


class RouterEmptyException(Exception):
    pass


class HttpServer(object):

    def __init__(self, event_loop, url_views, keepalive=False):
        self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        flags = fcntl.fcntl(self.s_socket.fileno(), fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(self.s_socket.fileno(), fcntl.F_SETFD)
        self.s_socket.setblocking(0)
        self.s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.event_loop = event_loop
        if not url_views:
            raise RouterEmptyException
        self.url_views = url_views
        self.keepalive = keepalive

    def bind(self, host="localhost", port=80):
        self.s_socket.bind((host, port))

    def listen(self, size=128):
        self.s_socket.listen(size)

    def start(self, num_processes=1):
        if (num_processes is None) or (num_processes <= 0):
            num_processes = os.cpu_count()
        if num_processes > 1:
            for _ in range(num_processes):
                pid = os.fork()
                if pid == -1:
                    raise OSError
                elif pid == 0:
                    self.event_loop.add_handler(self.s_socket.fileno(),
                                                EventLoop.READ,
                                                self.handle_event)
                    return
                else:
                    os.waitpid(-1, 0)
        else:
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
        Stream(c_socket, self.event_loop, self.url_views, self.keepalive)
