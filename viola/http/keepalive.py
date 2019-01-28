# encoding=utf8
import socket
import weakref
from threading import Timer


class KeepAlive(object):
    TCP_KEEPALIVE = 5
    connections = weakref.WeakValueDictionary()

    @classmethod
    def not_exists(cls, conn):
        if not KeepAlive.connections.get(id(conn)):
            KeepAlive.connections[id(conn)] = conn
            return True
        else:
            return False

    def __init__(self, conn, event_loop, timeout=0.05, max_count=1000):
        self.conn = conn
        self.event_loop = event_loop
        self.timeout = timeout
        self.max_count = max_count
        # TCP Keep-Alive
        tcp_keepalive = self.conn.getsockopt(socket.SOL_SOCKET,
                                             socket.SO_KEEPALIVE)
        if tcp_keepalive == 0:
            self.conn.setsockopt(socket.SOL_SOCKET,
                                 socket.SO_KEEPALIVE,
                                 KeepAlive.TCP_KEEPALIVE)
        Timer(self.timeout, self.close_conn).start()    # Replace to `scheduler`

    def close_conn(self):
        self.event_loop.remove_handler(self.conn.fileno())
        self.conn.close()
