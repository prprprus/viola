from viola.epoll import Epoll


class EventsEmptyException(Exception):
    pass


class EventLoop(object):
    """A epoll-based event loop. Use edge trigger mode of epoll"""
    # Constant of EventLoop
    READ = Epoll.READ
    WRITE = Epoll.WRITE
    ERROR = Epoll.ERROR
    ET = Epoll.ET

    def __init__(self):
        self.epoll = Epoll()
        self.handlers = {}
        self.timeout = 0.2

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def add_handler(self, fd, events, handler):
        """Register listen fd to epoll and add handler"""
        # Addition of EventLoop.ERROR for events
        if not events:
            # print("events is empty")
            raise EventsEmptyException
        self.epoll.register(fd, events | EventLoop.ERROR | EventLoop.ET)
        self.handlers[fd] = handler
        # print("[add_handler]", self.handlers)

    def remove_handler(self, fd):
        """Unregister listen fd from epoll and remove handler"""
        self.epoll.unregister(fd)
        self.handlers.pop(fd)
        # print("[remove_handler]", self.handlers)

    def update_handler(self, fd, events):
        """Update interested event of fd"""
        if not events:
            # print("events is empty")
            raise EventsEmptyException
        self.epoll.modify(fd, events | EventLoop.ERROR | EventLoop.ET)
        # print("[update_handler]", self.handlers)

    def start(self):
        while True:
            events = self.epoll.poll(self.timeout)
            for fd, event in events:
                # Run httpserver's `_handler_event` callback method
                self.handlers[fd](fd, event)

    def stop(self):
        pass
