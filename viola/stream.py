# encoding=utf8
import collections


class Stream(object):
    def __init__(self, c_socket):
        self.c_socket = c_socket
        self.read_buffer = collections.deque()
