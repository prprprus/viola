# encoding=utf8
import collections
from viola.event_loop import EventLoop
from viola.http.handler import HttpHandler
from viola.http.keepalive import KeepAlive
import socket
from viola.exception import ViolaEventException


class Stream(object):
    def __init__(self, c_socket, event_loop, url_views, keepalive,
                 max_buffer_size=104857600, chunk_size=4096):
        self.c_socket = c_socket
        self.c_socket.setblocking(0)
        self.event_loop = event_loop
        self.url_views = url_views
        self.keepalive = keepalive
        self.read_buffer = collections.deque()
        self.wrough_rebuff = collections.deque()
        self.write_buffer = collections.deque()
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
            # print(1)
            self.handle_read()
            # 将读写处理完毕的 stream 丢给 `http_handler`
            if self.read_buffer or self.wrough_rebuff:
                self.read_from_buffer(self.read_buffer)
                HttpHandler(self, self.event_loop, self.url_views,
                            self.wrough_rebuff[0])
                self.wrough_rebuff.popleft()
            # 由于读数据时是采取尽可能多的读, 没有使用把请求分开一个一个地读, 所以当请求的数据量远远小于 chunk_size 时,
            # 很容易会发生一次读就读了若干个请求数据, 剩下的读就绪事件没数据可以读, 就会造成读就绪事件饥饿.
            # 这里的 `break` 就是为了防止读就绪事件饥饿.
            # (现象就是大量饥饿的读就绪事件造成 CPU 飙高, 从而造成服务器无法处理后续的请求. 可以通过连续疯狂 ab 来重现这个现象)
            else:
                self.release()
        elif event & EventLoop.WRITE:
            # print(2)
            self.handle_write()
        # 怎么处理?
        elif event & EventLoop.ERROR:
            # print("epoll error, close it")
            self.release()
            raise
        else:
            self.release()
            raise ViolaEventException

    def handle_read(self):
        try:
            # 默认读一次就是一个完整的请求
            chunk = self.c_socket.recv(self.chunk_size)
            if len(chunk) > 0:
                self.read_buffer.append(chunk)
        except BlockingIOError:
            # print("ViolaReadBlockingIOError ignore it")
            pass
        except (ConnectionResetError,
                BrokenPipeError):
            # print("ViolaReadConnectionResetError")
            self.release()
        except:
            # print("c_socket recv error, close it")
            self.release()
            raise

    def handle_write(self):
        try:
            while self.write_buffer:
                data = self.write_buffer[0]
                # 判断发送缓冲区和 write_buffer 大小关系
                if len(data) <= self.sndbuff:
                    self.c_socket.send(data)
                    self.write_buffer.popleft()
                else:
                    size = self.c_socket.send(data)
                    self.write_buffer[0] = self.write_buffer[0][size:]
        except BlockingIOError:
            # print("ViolaWriteBlockingIOError ignore it")
            pass
        except (ConnectionResetError,
                BrokenPipeError):
            # print("ViolaWriteConnectionResetError, ViolaBrokenPipeError")
            self.release()
        except:
            # print("c_socket send error, close it")
            self.release()
            raise
        finally:
            if self.keepalive:
                # 数据没写完则不修改监听事件
                if not self.write_buffer:
                    events = EventLoop.READ
                    self.event_loop.update_handler(self.c_socket.fileno(),
                                                   events)
                if KeepAlive.not_exists(self.c_socket):
                    # 若客户端出现异常, 则异常处理已经关闭了连接. 这里也就无需再 KeepAlive
                    try:
                        KeepAlive(self.c_socket, self.event_loop)
                    except OSError:
                        pass
            else:
                # 若是大文件, 数据一般需要写多次, 则先不关闭连接
                if not self.write_buffer:
                    self.release()

    def release(self):
        self.event_loop.remove_handler(self.c_socket.fileno())
        self.c_socket.close()

    def read_from_buffer(self, read_buffer):
        """整理出完整的 GET 请求"""
        # GET
        delimiter = "\r\n\r\n"
        if read_buffer:
            str_rebuff = ""
            for rb in self.read_buffer:
                str_rebuff += rb.decode("utf8")
            # 过滤 `split()` 后的 "" 字符串
            [self.wrough_rebuff.append(x) for x in str_rebuff.split(delimiter)
             if x.replace(" ", "")]
        # POST
        # TODO
