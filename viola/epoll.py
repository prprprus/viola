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
        self._epfd = _poll()

    def fileno(self):
        return self._epfd.fileno()

    def register(self, fd, events=select.EPOLLIN):
        """For `EPOLL_CTL_ADD`"""
        self._epfd.register(fd, events)

    def unregister(self, fd):
        """For `EPOLL_CTL_DEL`"""
        self._epfd.unregister(fd)

    def modify(self, fd, events):
        """For `EPOLL_CTL_MOD`"""
        self._epfd.modify(fd, events)

    def poll(self, timeout=-1):
        """For `epoll_wait`"""
        return self._epfd.poll(timeout)
