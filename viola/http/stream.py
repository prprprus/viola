from viola.stream import TCPStream
from viola.exception import ViolaEventException
from viola.event_loop import EventLoop


class HTTPStream(TCPStream):
    def __init__(self, c_socket, event_loop, req_handler, keepalive):
        super(HTTPStream, self).__init__(c_socket, event_loop, keepalive)
        self.req_handler = req_handler

    def handle_event(self, fd, event):
        if event & EventLoop.READ:
            self.handle_read()
            if self.read_buffer or self.wrough_rebuff:
                self.read_from_buffer(self.read_buffer)
                resp_data = self.req_handler()
                self.write_buffer.append(resp_data)
                self.event_loop.update_handler(self.c_socket.fileno(),
                                               EventLoop.WRITE)
                self.wrough_rebuff.popleft()
            else:
                self.release()
        elif event & EventLoop.WRITE:
            self.handle_write()
        elif event & EventLoop.ERROR:
            # print("epoll error, close it")
            self.release()
            raise
        else:
            self.release()
            raise ViolaEventException
