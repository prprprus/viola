import select
import logging


try:
    poll = select.epoll
except ImportError:
    logging.error("Your system does not support epoll")
    raise


class Epoll(object):
    READ = select.EPOLLIN
    WRITE = select.EPOLLOUT
    ERROR = select.EPOLLERR | select.EPOLLHUP | select.EPOLLRDHUP
    ET = select.EPOLLET

    def __init__(self):
        self.epfd = poll()  # epoll_create

    def fileno(self):
        return self.epfd.fileno()

    def register(self, fd, events):
        self.epfd.register(fd, events)  # epoll_ctl_add

    def unregister(self, fd):
        self.epfd.unregister(fd)    # epoll_ctl_del

    def modify(self, fd, events):
        self.epfd.modify(fd, events)    # epoll_ctl_mod

    def poll(self, timeout=-1):
        return self.epfd.poll(timeout)  # epoll_wait
