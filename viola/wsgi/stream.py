from viola.stream import TCPStream
from viola.exception import ViolaEventException
from viola.event_loop import EventLoop
from viola.http.parser import Parser
from viola.http.wrapper import Wrapper
import logging


class WSGIStream(TCPStream):
    def __init__(self, c_socket, event_loop, wsgi_handler, start_response,
                 keepalive=False):
        super(WSGIStream, self).__init__(c_socket, event_loop, keepalive)
        self.wsgi_handler = wsgi_handler
        self.start_response = start_response

    def handle_event(self, fd, event):
        """Handle already event for connection socket"""
        if event & EventLoop.READ:
            self.handle_read()
            if self.read_buffer:
                # Parse request
                env = Parser(self.read_buffer).get_environ()
                # Run wsgi handler
                resp_data = self.wsgi_handler(env, self.start_response)
                # Wrapper response
                [self.write_buffer.append(Wrapper(x, env).get_resp())
                 for x in resp_data]
                # Change listen event to write
                self.event_loop.update_handler(self.c_socket.fileno(),
                                               EventLoop.WRITE)
        elif event & EventLoop.WRITE:
            self.handle_write()
        elif event & EventLoop.ERROR:
            logging.error("class WSGIStream handle_event error, close it")
            self.release()
            raise
        else:
            self.release()
            raise ViolaEventException
