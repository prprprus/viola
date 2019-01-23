# encoding=utf8
import socket
from viola.event_loop import EventLoop
import fcntl
import os
import time
from threading import Timer
from functools import partial


class HttpServer(object):

    def __init__(self):
        self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        flags = fcntl.fcntl(self.s_socket.fileno(), fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(self.s_socket.fileno(), fcntl.F_SETFD)
        self.s_socket.setblocking(0)
        self.s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.event_loop = EventLoop.instance()
        self.connections = {}

    def bind(self, host="localhost", port=80):
        self.s_socket.bind((host, port))

    def listen(self, size=128):
        self.s_socket.listen(size)
        self.start()    # httpserver start here

    def start(self):
        self.event_loop.add_handler(self.s_socket.fileno(), EventLoop.READ,
                                    self._handle_event)

    def stop(self):
        pass

    def _handle_event(self, fd, event):
        # 这里必须要 `accept()` 不然水平触发会一直通知. CPU 使用会狂飙
        c_socket, address = self.s_socket.accept()
        c_socket.setblocking(0)
        events = EventLoop.READ
        self.event_loop.add_handler(c_socket.fileno(), events,
                                    self._handle_connection)
        print(c_socket, c_socket.fileno())
        # 这里如果不把  c_socket 保存起来, 函数结束后将会释放掉
        # 客户端再发送自然会报 104 错误
        self.connections[c_socket.fileno()] = c_socket

    def _handle_connection(self, fd, event):
        if event & EventLoop.READ:
            chuck = self.connections[fd].recv(8192)
            # 判断是否读取结束(直到读到 0 个字节为止)
            while len(chuck) > 0:
                try:
                    chuck += self.connections[fd].recv(8192)
                except BlockingIOError:
                    break
            # 输出最终的读取结果
            print(chuck)

            # 关闭连接. 否则读就绪事件会一直通知
            # self.connections[fd].close()
            # print("read finished, close socket.")
            # return
            # 尝试不关闭 socket 而是将事件改成写感兴趣
            events = EventLoop.WRITE
            self.event_loop.update_handler(fd, events)
            return
        elif event & EventLoop.WRITE:
            print(fd, event)
            print("fuxk")
            self.connections[fd].sendall(b"111")    # b"111" 换成动态的消息
            self.connections[fd].shutdown(socket.SHUT_RDWR)    # ?
            self.connections[fd].close()    # keep-alive 就是这里不关闭. 而是将写感兴趣又改成读感兴趣
        elif event & EventLoop.ERROR:
            print("fuxk error")


if __name__ == '__main__':
    server = HttpServer()
    server.bind(port=2333)
    server.listen()
    event_loop = EventLoop.instance()
    event_loop.start()
