# encoding=utf8
import collections
from viola.event_loop import EventLoop
from viola.http.handler import HttpHandler
from viola.http.keepalive import KeepAlive
import socket


class EventException(Exception):
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
        self.sndbuff = self.c_socket.getsockopt(socket.SOL_SOCKET,
                                                socket.SO_SNDBUF)
        self.revbuff = self.c_socket.getsockopt(socket.SOL_SOCKET,
                                                socket.SO_RCVBUF)

    def handle_event(self, fd, event):
        if event & EventLoop.READ:
            self.handle_read()
            # 将读写处理完毕的 stream 丢给 `http_handler`
            # 异常处理?
            if self.read_buffer:
                HttpHandler(self, self.event_loop, self.url_views)
        elif event & EventLoop.WRITE:
            self.handle_write()
        # 怎么处理?
        elif event & EventLoop.ERROR:
            # print("epoll error, close it")
            self.recycle()
            raise
        else:
            self.recycle()
            raise EventException

    def handle_read(self):
        while True:
            try:
                chunk = self.c_socket.recv(self.chunk_size)
            except BlockingIOError:
                # print("Read BlockingIOError ignore it")
                break
            # KEEPALIVE 且高并发下客户端可能会关闭连接(如果 ab 压测时)
            except ConnectionResetError:
                # print("Read ConnectionResetError")
                self.recycle()
                # break 防止 ConnectionResetError 造成的 UnboundLocalError:
                # local variable 'chunk' referenced before assignment 异常
                break
            except:
                # print("c_socket recv error, close it")
                self.recycle()
                raise
            if len(chunk) > 0:
                self.read_buffer.append(chunk)
            else:
                break

    def handle_write(self):
        try:
            while self.write_buffer:
                data = self.write_buffer[0]
                # 判断发送缓冲区和 write_buffer 大小关系
                if len(data) <= self.sndbuff:
                    print("jio...")
                    self.c_socket.send(data)
                    self.write_buffer.popleft()
                else:
                    size = self.c_socket.send(data)
                    self.write_buffer[0] = self.write_buffer[0][size:]
                    # print("fuxk")
                    # print(size)
        except BlockingIOError: # sndbuff 满了
            # print("Write BlockingIOError ignore it")
            pass
        except ConnectionResetError, BrokenPipeError:   # 客户端异常关闭了连接
            # print("Write ConnectionResetError, BrokenPipeError")
            self.recycle()
        except:
            # print("c_socket send error, close it")
            self.recycle()
            raise
        finally:
            if self.keepalive:
                # 数据没写完则不修改监听事件
                if not self.write_buffer:
                    events = EventLoop.READ
                    self.event_loop.update_handler(self.c_socket.fileno(),
                                                   events)
                # 若客户端出现异常, 则异常处理已经关闭了连接. 这里也就无需再 KeepAlive
                if (self.c_socket.fileno() != -1) and \
                        KeepAlive.not_exists(self.c_socket):
                    KeepAlive(self.c_socket, self.event_loop)
            else:
                # 若是大文件, 数据一般需要写多次, 则先不关闭连接
                if not self.write_buffer:
                    self.recycle()

    def recycle(self):
        self.event_loop.remove_handler(self.c_socket.fileno())
        self.c_socket.close()
