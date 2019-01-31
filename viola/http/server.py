from viola.server import TCPServer
from viola.http.stream import HTTPStream


class HTTPServer(TCPServer):
    def __init__(self, event_loop, keepalive=False):
        super(HTTPServer, self).__init__(event_loop, keepalive)

    def handle_event(self, fd, event):
        try:
            c_socket, address = self.s_socket.accept()
        except:
            print("accept error, close it")
            c_socket.close()
            raise
        HTTPStream(c_socket, self.event_loop, self.req_handler,
                   keepalive=self.keepalive)
