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
        """"Equivalent epoll_create"""
        self.epfd = poll()

    def register(self, fd, events):
        """Equivalent epoll_ctl_add"""
        self.epfd.register(fd, events)

    def unregister(self, fd):
        """Equivalent epoll_ctl_del"""
        self.epfd.unregister(fd)

    def modify(self, fd, events):
        """Equivalent epoll_ctl_mod"""
        self.epfd.modify(fd, events)

    def poll(self, timeout=-1):
        """Equivalent epoll_wait"""
        return self.epfd.poll(timeout)

    def fileno(self):
        """File descriptor of epoll instance"""
        return self.epfd.fileno()
