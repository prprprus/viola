import select
# import logging


try:
    _poll = select.epoll
except ImportError:
    # logging.warning("epoll module not found")
    raise


class Epoll(object):
    """Wapper epoll"""
    # Constant of epoll
    READ = select.EPOLLIN
    WRITE = select.EPOLLOUT
    ERROR = select.EPOLLERR | select.EPOLLHUP | select.EPOLLRDHUP
    ET = select.EPOLLET    # option

    def __init__(self):
        # For `epoll_create`
        self.epfd = _poll()

    def fileno(self):
        return self.epfd.fileno()

    def register(self, fd, events=select.EPOLLIN):
        """For `epoll_ctl(EPOLL_CTL_ADD)`"""
        self.epfd.register(fd, events)
        # ET example
        # self.epfd.register(fd, events | Epoll.ET)

    def unregister(self, fd):
        """For `epoll_ctl(EPOLL_CTL_DEL)`"""
        self.epfd.unregister(fd)

    def modify(self, fd, events):
        """For `epoll_ctl(EPOLL_CTL_MOD)`"""
        self.epfd.modify(fd, events)

    def poll(self, timeout=-1):
        """For `epoll_wait`"""
        return self.epfd.poll(timeout)
