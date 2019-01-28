# encoding=utf8
import collections
from viola.event_loop import EventLoop
from viola.http.handler import HttpHandler
from viola.http.keepalive import KeepAlive


class EventNotExistsException(Exception):
    pass


class Stream(object):
    def __init__(self, c_socket, event_loop, url_views, keepalive,
                 max_buffer_size=104857600, chunk_size=4096):
        self.c_socket = c_socket
        self.c_socket.setblocking(0)
        self.event_loop = event_loop
        self.url_views = url_views
        self.keepalive = keepalive
        self.read_buffer = collections.deque()    # HTTP request read buffer
        self.write_buffer = collections.deque()    # HTTP response write buffer
        self.chunk_size = chunk_size
        self.max_buffer_size = max_buffer_size
        events = EventLoop.READ
        self.event_loop.add_handler(self.c_socket.fileno(), events,
                                    self.handle_event)

    def handle_event(self, fd, event):
        if event & EventLoop.READ:
            self.handle_read()
            # 将读写处理完毕的 stream 丢给 `http_handler`
            # 异常处理?
            if self.read_buffer:
                HttpHandler(self, self.event_loop, self.url_views)
        elif event & EventLoop.WRITE:
            self.handle_write()
        elif event & EventLoop.ERROR:
            print("epoll error, close it")
            self.handle_error()
            raise
        else:
            self.handle_error()
            raise EventNotExistsException

    def handle_read(self):
        """循环读直到读到 0 个字节或者读到 EGAIN 为止"""
        while True:
            try:
                chunk = self.c_socket.recv(self.chunk_size)
            except BlockingIOError:
                # print("BlockingIOError ignore it")
                break
            except:
                print("c_socket recv error, close it")
                self.handle_error()
                raise
            if len(chunk) > 0:
                self.read_buffer.append(chunk)
            else:
                break

    def handle_write(self):
        try:
            while self.write_buffer:
                self.c_socket.send(self.write_buffer[0])
                self.write_buffer.popleft()
        except:
            print("c_socket send error, close it")
            print('fuxk')
            raise
        finally:
            # keepalive
            if self.keepalive:
                events = EventLoop.READ
                self.event_loop.update_handler(self.c_socket.fileno(), events)
                if KeepAlive.not_exists(self.c_socket):
                    KeepAlive(self.c_socket, self.event_loop)
            else:
                self.handle_error()

    def handle_error(self):
        self.event_loop.remove_handler(self.c_socket.fileno())
        self.c_socket.close()
