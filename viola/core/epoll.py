import select
import logging


try:
    poll = select.epoll
except ImportError:
    logging.error("System does not support epoll")
    raise


class Epoll(object):
    READ = select.EPOLLIN
    WRITE = select.EPOLLOUT
    ERROR = select.EPOLLERR | select.EPOLLHUP | select.EPOLLRDHUP
    ET = select.EPOLLET

    def __init__(self):
        self.epfd = poll()

    def register(self, fd, events):
        self.epfd.register(fd, events)

    def unregister(self, fd):
        self.epfd.unregister(fd)

    def modify(self, fd, events):
        self.epfd.modify(fd, events)

    def poll(self, timeout=-1):
        return self.epfd.poll(timeout)

    def fileno(self):
        return self.epfd.fileno()
