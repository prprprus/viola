# encoding=utf8
import bisect
import time
from collections import deque


class Scheduler(object):

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.tasks = deque()    # Orderly queue
        self.running = False

    def add_task(self, deadline, callback):
        task = Task(deadline, self._wrap_callback(callback))
        bisect.insort(self.tasks, task)
        self.running = True

    def cancel(self):
        self.running = False

    def _wrap_callback(self, callback):
        if not self.running:
            # print("Task was canceled")
            return
        try:
            callback()
        except:
            # print("Callback error")
            raise


class Task(object):

    __slots__ = ["deadline", "callback"]

    def __init__(self, deadline, callback):
        self.deadline = time.time() + deadline   # millisecond
        self.callback = callback

    def __eq__(self, other):
        return self.deadline == other.deadline

    def __lt__(self, other):
        return self.deadline < other.deadline

    def __le__(self, other):
        return self.deadline <= other.deadline
