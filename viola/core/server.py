import socket
from viola.core.event_loop import EventLoop
import fcntl
import os
import logging


class TCPServer(object):

    def __init__(self, event_loop):
        """
        Standard creation process for server socket:
        Create server socket.
        Set file descriptor flags(close-on-exec) of server socket.
        Set server socket to non-blocking.
        Set TCP common option `SO_REUSEADDR`.
        """
        self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        flags = fcntl.fcntl(self.s_socket.fileno(), fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(self.s_socket.fileno(), fcntl.F_SETFD, flags)
        self.s_socket.setblocking(0)
        self.s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.event_loop = event_loop

    def bind(self, host="localhost", port=80):
        """Bind host and port to server socket"""
        self.s_socket.bind((host, port))

    def listen(self, size=128):
        """Set size of TCP accept queue"""
        self.s_socket.listen(size)

    def start(self, num_processes=1):
        """Start server. Create number of process based on number of CPUs"""
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
                    logging.debug("Subprocess: ", id(self.event_loop.epoll))
                    return
                else:
                    logging.debug("Parentprocess: ", id(self.event_loop.epoll))
                    os.waitpid(-1, 0)
        else:
            self.event_loop.add_handler(self.s_socket.fileno(), EventLoop.READ,
                                        self.handle_event)

    def stop(self):
        """Stop server"""
        self.event_loop.remove_handler(self.s_socket.fileno())
        self.s_socket.close()

    def handle_event(self, fd, event):
        """Left to the upper server implementation"""
        raise NotImplementedError

    def set_wsgi_app(self, wsgi_app):
        """Set wsgi application"""
        self.wsgi_app = wsgi_app
