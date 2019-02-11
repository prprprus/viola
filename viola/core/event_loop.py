from viola.core.epoll import Epoll
import time


class EventLoop(object):
    """A epoll-based event loop. Use LT mode of epoll"""
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
        self._stop = False
        self._running = False

    def add_handler(self, fd, events, handler):
        """
        Register listen fd to epoll and add handler to fd.
        Additional EventLoop.ERROR for events.
        """
        self.epoll.register(fd, events | EventLoop.ERROR)
        self.handlers[fd] = handler

    def remove_handler(self, fd):
        """Unregister listen fd from epoll and remove handler"""
        self.epoll.unregister(fd)
        self.handlers.pop(fd)

    def update_handler(self, fd, events):
        """Update interested event for fd"""
        self.epoll.modify(fd, events | EventLoop.ERROR)

    def start(self):
        """Start event loop"""
        if self._stop:
            self._stop = False
            return
        self._running = True

        while True:
            poll_timeout = 0.2

            # Run callback task: TODO
            pass

            # Run scheduler task
            now = time.time()
            while self.scheduler.tasks and \
                    (self.scheduler.tasks[0].deadline <= now):
                self.scheduler.tasks[0].callback()  # TODO: Add try-catch
                self.scheduler.tasks.popleft()
            if self.scheduler.tasks:
                interval = self.scheduler.tasks[0].deadline - now
                # Priority to run task if interval less than epoll timeout
                # because you need to make task as punctual as possible.
                poll_timeout = min(interval, poll_timeout)

            # If stop event loop in somewhere, exit the event loop
            if not self._running:
                break

            events = self.epoll.poll(poll_timeout)  # epoll_wait
            for fd, event in events:
                self.handlers[fd](fd, event)

    def stop(self):
        """Stop event loop"""
        self._stop = True
        self._running = False

    def get_status(self):
        """Get event loop status"""
        return "running" if self._running else "stopped"
