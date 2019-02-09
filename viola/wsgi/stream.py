from viola.stream import TCPStream
from viola.exception import ViolaEventException
from viola.event_loop import EventLoop
from viola.http.parser import Parser


class WSGIStream(TCPStream):
    def __init__(self, c_socket, event_loop, wsgi_handler, start_response,
                 keepalive=False):
        super(WSGIStream, self).__init__(c_socket, event_loop, keepalive)
        self.wsgi_handler = wsgi_handler
        self.start_response = start_response

    def handle_event(self, fd, event):
        if event & EventLoop.READ:
            self.read_from_socket()
            if self.read_buffer or self.wrough_rebuff:
                env = Parser.read_from_buffer(self.read_buffer,
                                              self.wrough_rebuff)
                # Run wsgi handler
                resp_data = self.wsgi_handler(env, self.start_response)
                # Change listen event to write
                [self.write_buffer.append(x) for x in resp_data]
                self.event_loop.update_handler(self.c_socket.fileno(),
                                               EventLoop.WRITE)
                self.wrough_rebuff.popleft()
            # Prevent event of read hunger
            else:
                self.release()
        elif event & EventLoop.WRITE:
            self.write_to_socket()
        elif event & EventLoop.ERROR:
            # print("epoll error, close it")
            self.release()
            raise
        else:
            self.release()
            raise ViolaEventException
