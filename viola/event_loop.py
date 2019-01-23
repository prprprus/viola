from viola.epoll import Epoll


class EventLoop(object):
    """A epoll-based event lopp"""
    # Constant of EventLoop
    READ = Epoll.READ
    WRITE = Epoll.WRITE
    ERROR = Epoll.ERROR
    ET = Epoll.ET

    def __init__(self):
        self._epoll = Epoll()
        self.handlers = {}
        self.timeout = 0.2

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, "el_instance"):
            cls.el_instance = cls()
        return cls.el_instance

    def add_handler(self, fd, events, handler):
        """Register listen fd to epoll and add handler"""
        # Addition of EventLoop.ERROR for events
        self._epoll.register(fd, events | EventLoop.ERROR)
        self.handlers[fd] = handler
        print("add_handler: ", self.handlers)

    def remove_handler(self, fd):
        """Unregister listen fd from epoll and remove handler"""
        self._epoll.unregister(fd)
        self.handlers.pop(fd)
        print("remove_handler: ", self.handlers)

    def update_handler(self, fd, events):
        """Update interested event of fd"""
        self._epoll.modify(fd, events | EventLoop.ERROR)
        print("update_handler: ", self.handlers)

    def start(self):
        while True:
            events = self._epoll.poll(self.timeout)
            for fd, event in events:
                # Run httpserver's `_handler_event()` callback method
                self.handlers[fd](fd, event)

    def stop(self):
        pass
