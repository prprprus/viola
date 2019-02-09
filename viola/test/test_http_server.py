from viola.event_loop import EventLoop
from viola.http.server import HTTPServer
from viola.scheduler import Scheduler
from viola.test.test_http_app import app
import os


if __name__ == '__main__':
    event_loop = EventLoop.instance(Scheduler.instance())
    server = HTTPServer(event_loop)
    # server = HTTPServer(event_loop, keepalive=True)
    server.set_handler(app)
    server.bind(host="10.211.55.25", port=2333)
    server.listen(9128)
    server.start(os.cpu_count())
    # server.start(1)
    event_loop.start()
