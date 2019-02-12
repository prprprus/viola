from viola.core.server import TCPServer
from viola.wsgi.stream import WSGIStream
import logging


class WSGIServer(TCPServer):
    def __init__(self, event_loop):
        super(WSGIServer, self).__init__(event_loop)

    def handle_event(self, fd, event):
        try:
            c_socket, address = self.s_socket.accept()
            self.c_socket = c_socket
        except:
            logging.debug("WSGIServer class handle_event error, close it")
            c_socket.close()
            raise
        WSGIStream(c_socket, self.event_loop, self.wsgi_app, self.start_response)

    def start_response(self, status, response_headers, exc_info=None):
        pass
