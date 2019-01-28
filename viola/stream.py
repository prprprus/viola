# encoding=utf8
import collections
from viola.event_loop import EventLoop
from viola.http.handler import HttpHandler
from viola.http.keepalive import KeepAlive


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
        # events 暂时这样处理
        events = EventLoop.READ
        self.event_loop.add_handler(self.c_socket.fileno(), events,
                                    self.handle_event)

    def handle_event(self, fd, event):
        try:
            if event & EventLoop.READ:
                self.handle_read()
                # 将读写处理完毕的 stream 丢给 `http_handler`
                HttpHandler(self, self.event_loop, self.url_views).route()
            elif event & EventLoop.WRITE:
                self.handle_write()
            elif event & EventLoop.ERROR:
                print("epoll error, close it")
                self.c_socket.close()
                raise
        except:
            print("c_socket error, close it")
            self.c_socket.close()
            raise

    def handle_read(self):
        """循环读直到读到 0 个字节为止"""
        while True:
            try:
                chunk = self.c_socket.recv(self.chunk_size)
            except BlockingIOError:
                # print("BlockingIOError ignore it")
                break
            except:
                print("c_socket recv error, close it")
                self.c_socket.close()
                raise
            if len(chunk) > 0:
                self.read_buffer.append(chunk)
            else:
                break

    def handle_write(self):
        try:
            while self.write_buffer:
                # resp_data = self.write_buffer.popleft()
                # self.c_socket.sendall(resp_data.encode("utf8"))
                self.c_socket.send(self.write_buffer[0])
                self.write_buffer.popleft()
        except:
            print("c_socket sendall error, close it")
            print('fuxk')
            self.c_socket.close()
            raise
        finally:
            try:
                if self.keepalive:
                    # 设置成读监听. 结合 Keep-Alive 重复利用 TCP 连接
                    events = EventLoop.READ
                    self.event_loop.update_handler(self.c_socket.fileno(), events)
                    if KeepAlive.not_exists(self.c_socket):
                        KeepAlive(self.c_socket, self.event_loop)
                else:
                    self.event_loop.remove_handler(self.c_socket.fileno())
                    self.c_socket.close()
            except:
                raise
        # print(self.event_loop.handlers)

    def handle_error(self):
        self.event_loop.remove_handler(self.c_socket.fileno())
        self.c_socket.close()

# def _handle_connection(self, fd, event):
#         if event & EventLoop.READ:
#             chuck = self.connections[fd].recv(8192)
#             # 判断是否读取结束(直到读到 0 个字节为止)
#             while len(chuck) > 0:
#                 try:
#                     chuck += self.connections[fd].recv(8192)
#                 except BlockingIOError:
#                     break
#             # 输出最终的读取结果
#             print(chuck)

#             # 关闭连接. 否则读就绪事件会一直通知
#             # self.connections[fd].close()
#             # print("read finished, close socket.")
#             # return
#             # 尝试不关闭 socket 而是将事件改成写感兴趣
#             events = EventLoop.WRITE
#             self.event_loop.update_handler(fd, events)
#             return
#         elif event & EventLoop.WRITE:
#             print(fd, event)
#             print("fuxk")
#             self.connections[fd].sendall(b"111")    # b"111" 换成动态的消息
#             self.connections[fd].shutdown(socket.SHUT_RDWR)    # ?
#             self.connections[fd].close()    # keep-alive 就是这里不关闭. 而是将写感兴趣又改成读感兴趣
#         elif event & EventLoop.ERROR:
#             print("fuxk error")
