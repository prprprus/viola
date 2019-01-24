import select
# import logging


try:
    poll = select.epoll
except ImportError:
    # logging.warning("epoll module not found")
    raise


class Epoll(object):
    """Wapper epoll"""
    # Constant of epoll
    READ = select.EPOLLIN
    WRITE = select.EPOLLOUT
    ERROR = select.EPOLLERR | select.EPOLLHUP | select.EPOLLRDHUP
    ET = select.EPOLLET

    def __init__(self):
        # For `epoll_create`
        self.epfd = poll()

    def fileno(self):
        return self.epfd.fileno()

    def register(self, fd, events):
        """For `EPOLL_CTL_ADD`"""
        self.epfd.register(fd, events)

    def unregister(self, fd):
        """For `EPOLL_CTL_DEL`"""
        self.epfd.unregister(fd)

    def modify(self, fd, events):
        """For `EPOLL_CTL_MOD`"""
        self.epfd.modify(fd, events)

    def poll(self, timeout=-1):
        """For `epoll_wait`"""
        return self.epfd.poll(timeout)
