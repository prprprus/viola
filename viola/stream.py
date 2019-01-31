# encoding=utf8
import collections
from viola.event_loop import EventLoop
from viola.http.keepalive import KeepAlive
import socket
from viola.exception import ViolaSendDataTypeException


class TCPStream(object):
    def __init__(self, c_socket, event_loop, keepalive,
                 max_buffer_size=104857600, chunk_size=4096):
        self.c_socket = c_socket
        self.c_socket.setblocking(0)
        self.event_loop = event_loop
        self.keepalive = keepalive
        self.read_buffer = collections.deque()
        self.wrough_rebuff = collections.deque()
        self.write_buffer = collections.deque()
        self.chunk_size = chunk_size
        self.max_buffer_size = max_buffer_size
        self.event_loop.add_handler(self.c_socket.fileno(), EventLoop.READ,
                                    self.handle_event)
        self.sndbuff = self.c_socket.getsockopt(socket.SOL_SOCKET,
                                                socket.SO_SNDBUF)
        self.revbuff = self.c_socket.getsockopt(socket.SOL_SOCKET,
                                                socket.SO_RCVBUF)

    def handle_event(self, fd, event):
        raise NotImplementedError

    def handle_read(self):
        try:
            while True:
                chunk = self.c_socket.recv(self.chunk_size)
                if len(chunk) > 0:
                    self.read_buffer.append(chunk)
                else:
                    break    # chunk 等于 '' 时主动退出循环
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
                data = self._repair(self.write_buffer[0])
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
                    self.event_loop.update_handler(self.c_socket.fileno(),
                                                   EventLoop.READ)
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
        """
        整理出完整的 GET 请求.
        这个函数应该从该模块移除, 放到别处
        """
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

    def _repair(self, data):
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode("utf8")
        elif isinstance(data, int) or isinstance(data, float):
            return str(data).encode("utf8")
        else:
            raise ViolaSendDataTypeException
