import collections
from viola.event_loop import EventLoop
import socket
from viola.exception import ViolaSendDataTypeException
import logging


class TCPStream(object):
    """Wrapper connection socket and register to event loop"""
    def __init__(self, c_socket, event_loop, max_buffer_size=104857600,
                 chunk_size=4096):
        self.c_socket = c_socket
        self.c_socket.setblocking(0)
        self.event_loop = event_loop
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
        """Left to the upper server implementation"""
        raise NotImplementedError

    def handle_read(self):
        """Read until TCP receive buffer empty or encounter exception"""
        try:
            while True:
                chunk = self.c_socket.recv(self.chunk_size)
                if len(chunk) > 0:
                    self.read_buffer.append(chunk)
                else:
                    break    # Exit the loop if chunk equal `''`
        except BlockingIOError:
            logging.debug("BlockingIOError, ignore it")
            pass
        except (ConnectionResetError, BrokenPipeError):
            logging.debug("Client exceptions")
            self.release()
        except:
            logging.error("`handle_read()` error, close it")
            self.release()
            raise

    def handle_write(self):
        """
        Write until pending buffer(`write_buffer`) empty or encounter exception
        """
        try:
            while self.write_buffer:
                data = self._repair(self.write_buffer[0])
                if len(data) <= self.sndbuff:   # Compare send buffer and data
                    self.c_socket.send(data)
                    self.write_buffer.popleft()
                else:
                    size = self.c_socket.send(data)
                    self.write_buffer[0] = self.write_buffer[0][size:]
        except BlockingIOError:
            logging.debug("BlockingIOError, ignore it")
            pass
        except (ConnectionResetError, BrokenPipeError):
            logging.debug("Client exceptions")
            self.release()
        except:
            logging.error("handle_write error, close it")
            self.release()
            raise
        finally:
            if not self.write_buffer:   # Big size file
                self.release()

    def release(self):
        """Release connection socket related resources"""
        try:
            self.event_loop.remove_handler(self.c_socket.fileno())
            self.c_socket.close()
        except:
            logging.error("release error.")
            pass

    def _repair(self, data):
        """Makesure correct for type of response data"""
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode("utf8")
        elif isinstance(data, int) or isinstance(data, float):
            return str(data).encode("utf8")
        else:
            raise ViolaSendDataTypeException
