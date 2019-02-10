import io
from viola.exception import (
    ViolaHTTPMethodException,
    ViolaHTTPVersionException
)


class Parser(object):
    HTTP_METHOD = ["OPTIONS", "GET", "HEAD", "POST",
                   "PUT", "DELETE", "TRACE", "CONNECT"]
    HTTP_VERSION = ["HTTP/1.1", "HTTP/1.0"]

    def __init__(self, http_req):
        self.http_req = http_req
        self.headers = {}
        self.env = {}

    def parse_request(self):
        self._parse_headers()
        self._parse_body()
        self._parse_mime_body()
        return {
            "headers": self.headers,
            "env": self.env
        }

    def _parse_headers(self):
        req_cont = io.StringIO(self.http_req)
        for line in req_cont.readlines():
            line = line.strip('\n').strip('\r')
            if line:
                # Parse frist line of headers
                if ':' not in line:
                    rows = line.split(' ')
                    self._parse_method(rows[0])
                    self._parse_arguments(rows[1])
                    self._parse_version(rows[2])
                else:
                    key, value = line.split(': ')
                    self.headers[key.strip()] = value.strip()
        self.env["headers"] = self.headers

    def _parse_method(self, method):
        if method not in Parser.HTTP_METHOD:
            raise ViolaHTTPMethodException
        self.headers["method"] = method

    def _parse_arguments(self, url):
        # HTTP GET arguments convert to dict
        if '?' not in url:
            self.headers["url"] = url
        else:
            self.headers["url"] = url.split('?')[0]
            args = [arg for arg in url.split('?')[1].split('&')]
            self.headers["arguments"] = \
                {arg.split('=')[0]: arg.split('=')[1] for arg in args}

    def _parse_version(self, version):
        if version not in Parser.HTTP_VERSION:
            raise ViolaHTTPVersionException
        self.headers["version"] = version

    def _parse_body(self):
        pass

    def _parse_mime_body(self):
        pass

    @classmethod
    def read_from_buffer(cls, read_buffer, wrough_rebuff):
        """Split HTTP requests"""
        # GET
        delimiter = "\r\n\r\n"
        if read_buffer:
            str_rebuff = ""
            for rb in read_buffer:
                str_rebuff += rb.decode("utf8")
            [wrough_rebuff.append(x) for x in str_rebuff.split(delimiter)
             if x.replace(" ", "")]
        # POST
        # TODO

        import sys
        env = {}
        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # Required WSGI variables
        env['wsgi.version']      = (1, 1)
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
