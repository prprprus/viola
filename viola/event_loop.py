"""A epoll-based event loop. Use LT trigger mode"""
from viola.epoll import Epoll
import time
from viola.exception import ViolaEventException


class EventLoop(object):
    READ = Epoll.READ
    WRITE = Epoll.WRITE
    ERROR = Epoll.ERROR
    ET = Epoll.ET

    @classmethod
    def instance(cls, scheduler):
        if not hasattr(cls, "_instance"):
            cls._instance = cls(scheduler)
        return cls._instance

    def __init__(self, scheduler):
        self.epoll = Epoll()
        self.handlers = {}
        self.scheduler = scheduler

    def add_handler(self, fd, events, handler):
        """
        Register listen fd to epoll and add handler.
        Additional EventLoop.ERROR for events
        """
        if not events:
            raise ViolaEventException
        self.epoll.register(fd, events | EventLoop.ERROR)
        self.handlers[fd] = handler

    def remove_handler(self, fd):
        """Unregister listen fd from epoll and remove handler"""
        self.epoll.unregister(fd)
        self.handlers.pop(fd)

    def update_handler(self, fd, events):
        """Update interested event for fd"""
        if not events:
            raise ViolaEventException
        self.epoll.modify(fd, events | EventLoop.ERROR)

    def start(self):
        while True:
            poll_timeout = 0.2
            now = time.time()
            while self.scheduler.tasks and \
                    (self.scheduler.tasks[0].deadline <= now):
                self.scheduler.tasks[0].callback()  # Add try-catch
                self.scheduler.tasks.popleft()

            # Priority run task if interval less than `timeout`
            if self.scheduler.tasks:
                interval = self.scheduler.tasks[0].deadline - now
                poll_timeout = min(interval, poll_timeout)

            events = self.epoll.poll(poll_timeout)
            for fd, event in events:
                self.handlers[fd](fd, event)    # Event already and run callback

    def stop(self):
        pass
