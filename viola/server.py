import socket
from viola.event_loop import EventLoop
import fcntl
import os


class TCPServer(object):

    def __init__(self, event_loop, keepalive=False):
        self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        flags = fcntl.fcntl(self.s_socket.fileno(), fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(self.s_socket.fileno(), fcntl.F_SETFD, flags)
        self.s_socket.setblocking(0)
        self.s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.event_loop = event_loop
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
                    # print("Subprocess: ", id(self.event_loop.epoll))
                    return
                else:
                    # print("Parentprocess: ", id(self.event_loop.epoll))
                    os.waitpid(-1, 0)
        else:
            self.event_loop.add_handler(self.s_socket.fileno(), EventLoop.READ,
                                        self.handle_event)

    def stop(self):
        self.event_loop.remove_handler(self.s_socket.fileno())
        self.s_socket.close()

    def handle_event(self, fd, event):
        raise NotImplementedError

    def set_handler(self, wsgi_handler):
        self.wsgi_handler = wsgi_handler
