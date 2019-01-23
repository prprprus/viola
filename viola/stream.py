# encoding=utf8
import collections


class Stream(object):
    def __init__(self, _c_socket):
        self._c_socket = _c_socket
        self._read_buffer = collections.deque()
