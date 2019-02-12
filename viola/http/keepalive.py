"""Not yet used for this module"""
import socket
import weakref


class KeepAlive(object):
    connections = weakref.WeakValueDictionary()

    @classmethod
    def not_exists(cls, stream):
        if not KeepAlive.connections.get(id(stream)):
            KeepAlive.connections[id(stream)] = stream
            return True
        else:
            return False

    def __init__(self, stream, event_loop, timeout=1, max_count=1000):
        self.stream = stream
        self.event_loop = event_loop
        self.timeout = timeout
        self.max_count = max_count
        # Makesure TCP keepalive option open
        tcp_keepalive = self.stream.c_socket.getsockopt(socket.SOL_SOCKET,
                                                        socket.SO_KEEPALIVE)
        if tcp_keepalive == 0:
            self.stream.c_socket.setsockopt(socket.SOL_SOCKET,
                                            socket.SO_KEEPALIVE, 5)

        self.event_loop.scheduler.add_task(self.timeout, self.stream.release)
