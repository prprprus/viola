import select


try:
    poll = select.epoll
except ImportError:
    # logging.warning("epoll module not found")
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
        self.epfd.register(fd, events)  # EPOLL_CTL_ADD

    def unregister(self, fd):
        self.epfd.unregister(fd)    # EPOLL_CTL_DEL

    def modify(self, fd, events):
        self.epfd.modify(fd, events)    # EPOLL_CTL_MOD

    def poll(self, timeout=-1):
        return self.epfd.poll(timeout)  # epoll_wait
