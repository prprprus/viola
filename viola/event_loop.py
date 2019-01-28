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

    @classmethod
    def instance(cls, scheduler):
        """Singleton mode"""
        if not hasattr(cls, "_instance"):
            cls._instance = cls(scheduler)
        return cls._instance

    def __init__(self, scheduler):
        self.epoll = Epoll()
        self.handlers = {}
        self.timeout = 0.2
        self.scheduler = scheduler

    def add_handler(self, fd, events, handler):
        """
        Register listen fd to epoll and add handler
        Addition of EventLoop.ERROR for events
        """
        if not events:
            raise EventsEmptyException
        self.epoll.register(fd, events | EventLoop.ERROR)
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
            raise EventsEmptyException
        self.epoll.modify(fd, events | EventLoop.ERROR)
        # print("[update_handler]", self.handlers)

    def start(self):
        print("-------------")
        print(self.scheduler.tasks)
        print(self.scheduler.running)
        print("-------------")
        while True:
            events = self.epoll.poll(self.timeout)
            for fd, event in events:
                # Run httpserver's `_handler_event`
                self.handlers[fd](fd, event)

    def stop(self):
        pass
