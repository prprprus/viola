# encoding=utf8
import socket
import weakref


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

    def __init__(self, conn, event_loop, timeout=1, max_count=1000):
        self.conn = conn
        self.event_loop = event_loop
        self.timeout = timeout
        self.max_count = max_count
        # 确保 TCP Keep-Alive 开启, HTTP Keep-Alive 才有意义
        tcp_keepalive = self.conn.getsockopt(socket.SOL_SOCKET,
                                             socket.SO_KEEPALIVE)
        if tcp_keepalive == 0:
            self.conn.setsockopt(socket.SOL_SOCKET,
                                 socket.SO_KEEPALIVE,
                                 KeepAlive.TCP_KEEPALIVE)
        self.event_loop.scheduler.add_task(self.timeout, self.close_conn)

    def close_conn(self):
        # `stream` 模块的 `handle_read()` 函数遇到 ConnectionResetError
        # 已经 `release()` 过, 因此这里会抛出 ValueError 异常, 需要捕获并忽略.
        try:
            self.event_loop.remove_handler(self.conn.fileno())
            self.conn.close()
        except ValueError:
            pass
