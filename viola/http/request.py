# encoding=utf8
"""
- 接收 handler 模块的输入: http_req
- 按照 HTTP 协议解析 http_req
- 将解析结果封装成 `HttpRequest` 对象并返回
"""
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
        """解析 HTTP 请求"""
        self._parse_headers()
        self._parse_body()
        self._parse_mime_body()
        return {
            "headers": self.headers,
            "env": self.env
        }

    def _parse_headers(self):
        """解析 HTTP header 信息"""
        req_cont = io.StringIO(self.http_req)
        for line in req_cont.readlines():
            line = line.strip('\n').strip('\r')
            if line:
                # 解析 HTTP headers 的第一行
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
        """解析请求方法"""
        if method not in Parser.HTTP_METHOD:
            raise ViolaHTTPMethodException
        self.headers["method"] = method

    def _parse_arguments(self, url):
        """解析参数并将参数转成字典形式"""
        if '?' not in url:
            self.headers["url"] = url
        else:
            self.headers["url"] = url.split('?')[0]
            args = [arg for arg in url.split('?')[1].split('&')]
            self.headers["arguments"] = \
                {arg.split('=')[0]: arg.split('=')[1] for arg in args}

    def _parse_version(self, version):
        """解析 HTTP 版本"""
        if version not in Parser.HTTP_VERSION:
            raise ViolaHTTPVersionException
        self.headers["version"] = version

    def _parse_body(self):
        pass

    def _parse_mime_body(self):
        pass


class HttpRequest(object):
    def __init__(self, http_req):
        self.http_req = http_req
        self.parser = Parser(self.http_req)
        result = self.parser.parse_request()
        self.headers = result["headers"]
        self.env = result["env"]
