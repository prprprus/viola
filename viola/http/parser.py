import io
from viola.exception import (
    ViolaHTTPMethodException,
    ViolaHTTPVersionException
)
import sys
import collections


class Parser(object):
    HTTP_METHOD = [
        "OPTIONS",
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "TRACE",
        "CONNECT"]
    HTTP_VERSION = [
        "HTTP/1.1",
        "HTTP/1.0"]

    def __init__(self, read_buffer):
        self.read_buffer = read_buffer
        self.headers = {}
        self.res = {}

    def parse_request(self):
        self._parse_headers()
        self._parse_body()
        self._parse_mime_body()
        return {
            "headers": self.headers,
            "res": self.res
        }

    def _parse_headers(self):
        req_cont = io.StringIO(self.read_buffer[0])
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
        self.res["headers"] = self.headers

    def _parse_method(self, method):
        if method not in Parser.HTTP_METHOD:
            raise ViolaHTTPMethodException
        self.headers["method"] = method

    def _parse_arguments(self, url):
        """HTTP GET arguments convert to dict"""
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

    def get_environ(self):
        """Split HTTP requests and return environment variable"""
        # Parse GET method
        delimiter = "\r\n\r\n"
        wrough_rebuff = collections.deque()
        if self.read_buffer:
            str_rebuff = ""
            for rb in self.read_buffer:
                str_rebuff += rb.decode("utf8")
            [wrough_rebuff.append(x) for x in str_rebuff.split(delimiter)
             if x.replace(" ", "")]
        self.read_buffer = wrough_rebuff
        res = self.parse_request()  # Parse HTTP request
        self.read_buffer.popleft()  # Consume

        # Parse POST method: TODO

        # WSGI environ Variables(Required)
        env = {}
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = b""
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = True
        env['wsgi.multiprocess'] = True
        env['wsgi.run_once']     = False
        env['REQUEST_METHOD']    = res["headers"]["method"]
        env['PATH_INFO']         = res["headers"]["url"]
        env['SERVER_NAME']       = res["headers"]["Host"].split(":")[0] if ":" in res["headers"]["Host"] else res["headers"]["Host"]
        env['SERVER_PORT']       = res["headers"]["Host"].split(":")[1] if ":" in res["headers"]["Host"] else "80"

        return env
