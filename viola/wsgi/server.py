from viola.server import TCPServer
from viola.wsgi.stream import WSGIStream


class WSGIServer(TCPServer):
    def __init__(self, event_loop, keepalive=False):
        super(WSGIServer, self).__init__(event_loop, keepalive)

    def handle_event(self, fd, event):
        try:
            c_socket, address = self.s_socket.accept()
            self.c_socket = c_socket
        except:
            print("accept error, close it")
            c_socket.close()
            raise

        WSGIStream(c_socket, self.event_loop, self.wsgi_handler,
                   self.start_response, keepalive=self.keepalive)

    def start_response(self, status, response_headers, exc_info=None):
        pass
