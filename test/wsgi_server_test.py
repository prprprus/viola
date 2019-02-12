from viola.core.event_loop import EventLoop
from viola.wsgi.server import WSGIServer
from viola.core.scheduler import Scheduler
# from wsgi_flask_test import app
from wsgi_bottle_test import app
# import os


if __name__ == '__main__':
    event_loop = EventLoop.instance(Scheduler.instance())
    server = WSGIServer(event_loop)
    server.set_wsgi_app(app)
    server.bind(host="10.211.55.25", port=2333)
    server.listen(9128)
    # server.start(os.cpu_count())
    server.start(1)
    event_loop.start()
