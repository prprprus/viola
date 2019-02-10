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
                    # Exit the loop if chunk equal `''`
                    break
        except BlockingIOError:
            # print("ViolaReadBlockingIOError ignore it")
            pass
        # Client exceptions
        except (ConnectionResetError, BrokenPipeError):
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
                # Compare send buffer and data
                if len(data) <= self.sndbuff:
                    self.c_socket.send(data)
                    self.write_buffer.popleft()
                else:
                    size = self.c_socket.send(data)
                    self.write_buffer[0] = self.write_buffer[0][size:]
        except BlockingIOError:
            # print("ViolaWriteBlockingIOError ignore it")
            pass
        # Client exceptions
        except (ConnectionResetError, BrokenPipeError):
            # print("ViolaWriteConnectionResetError, ViolaBrokenPipeError")
            self.release()
        except:
            # print("c_socket send error, close it")
            self.release()
            raise
        finally:
            if self.keepalive:
                # Do not change listen event if `write_buffer` not empty
                if not self.write_buffer:
                    self.event_loop.update_handler(self.c_socket.fileno(),
                                                   EventLoop.READ)
                if KeepAlive.not_exists(self):
                    # Do not need KeepAlive if client exceptions hanppen
                    try:
                        KeepAlive(self, self.event_loop)
                    except OSError:
                        pass
            else:
                # Big size file
                if not self.write_buffer:
                    self.release()

    def release(self):
        try:
            self.event_loop.remove_handler(self.c_socket.fileno())
            self.c_socket.close()
        except:
            # print("release error.")
            pass

    def _repair(self, data):
        """Makesure type of data correct"""
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode("utf8")
        elif isinstance(data, int) or isinstance(data, float):
            return str(data).encode("utf8")
        else:
            raise ViolaSendDataTypeException
