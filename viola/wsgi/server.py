from viola.http.server import HTTPServer
from viola.wsgi.stream import WSGIStream
import sys


def get_environ():
    env = {}
    # The following code snippet does not follow PEP8 conventions
    # but it's formatted the way it is for demonstration purposes
    # to emphasize the required variables and their values
    #
    # Required WSGI variables
    env['wsgi.version']      = (1, 0)
    env['wsgi.url_scheme']   = 'http'
    env['wsgi.input']        = b"hello world"
    env['wsgi.errors']       = sys.stderr
    env['wsgi.multithread']  = False
    env['wsgi.multiprocess'] = False
    env['wsgi.run_once']     = False
    # Required CGI variables
    env['REQUEST_METHOD']    = "GET"    # GET
    env['PATH_INFO']         = "/listNews"              # /hello
    env['SERVER_NAME']       = "10.211.55.25"       # localhost
    env['SERVER_PORT']       = "2333"  # 8888
    return env


class WSGIServer(HTTPServer):
    def __init__(self, event_loop, keepalive=False):
        super(WSGIServer, self).__init__(event_loop, keepalive)

    def handle_event(self, fd, event):
        try:
            c_socket, address = self.s_socket.accept()
        except:
            print("accept error, close it")
            c_socket.close()
            raise
        WSGIStream(c_socket, self.event_loop, self.wsgi_handler, get_environ(),
                   self.start_response, keepalive=self.keepalive)

    def start_response(self, status, response_headers, exc_info=None):
        server_headers = [
            ('Server', 'viola 0.26'),
        ]
        self.headers_set = [status, response_headers + server_headers]
